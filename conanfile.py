import os
from io import StringIO
from pathlib import Path

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class NativeFileDialogConan(ConanFile):
    name = "nativefiledialog"
    version = "116"
    description = "A tiny, neat C library that portably invokes native file open and save dialogs."
    topics = ("gui",)
    url = "https://github.com/rhololkeolke/conan-nativefiledialog"
    homepage = "https://github.com/mlabbe/nativefiledialog"
    author = "Devin Schwab <dschwab@andrew.cmu.edu>"
    license = "Zlib"
    exports = ["LICENSE.md"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"use_zenity": [True, False], "fPIC": [True, False]}
    default_options = {"use_zenity": False, "fPIC": True}

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux" and self.options.use_zenity:
            raise ConanInvalidConfiguration(
                "use_zenity=True is only valid for os=Linux"
            )

    def system_requirements(self):
        installer = tools.SystemPackageTool()

        if self.settings.os == "Linux" and not self.options.use_zenity:
            installer.install("libgtk-3-dev")

    def source(self):
        source_url = "https://github.com/mlabbe/nativefiledialog"
        tools.get(
            f"{source_url}/archive/release_{self.version}.tar.gz",
            sha256="1BBAED79B9C499C8D2A54F40F89277E721C0894BF3048BB247D826B96DB6BC08",
        )
        extracted_dir = f"{self.name}-release_{self.version}"

        os.rename(extracted_dir, self._source_subfolder)

    def _get_make_folder(self):
        make_folder = Path(self._source_subfolder) / "build"
        if self.settings.os == "Linux":
            if self.options.use_zenity:
                make_folder = make_folder / "gmake_linux_zenity"
            else:
                make_folder = make_folder / "gmake_linux"
        elif self.settings.os == "Windows":
            make_folder = make_folder / "gmake_windows"
        elif self.settings.os == "Macos":
            make_folder = make_folder / "gmake_macosx"

        return make_folder

    def build(self):
        make_folder = self._get_make_folder()
        if self.settings.build_type == "Debug":
            config = "debug_x64"
        else:
            config = "release_x64"
        self.run(f"make config={config} -C {make_folder}")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        include_folder = Path(self._source_subfolder) / "src" / "include"
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.use_zenity:
            pkgconfig_output_buf = StringIO()
            self.run("pkg-config --libs gtk+-3.0", output=pkgconfig_output_buf)

            pkgconfig_output = pkgconfig_output_buf.getvalue()
            pkgconfig_libs = pkgconfig_output.split(' ')

            gtk_libs = []
            for lib in pkgconfig_libs:
                # skip empty strings
                if lib == '':
                    continue
                gtk_libs.append(lib.split('-l')[1])

            self.cpp_info.libs.extend(gtk_libs)
