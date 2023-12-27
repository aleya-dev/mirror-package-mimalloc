from conan import ConanFile
from conan.tools.cmake import CMakeToolchain
from conan.tools.files import copy, rmdir, rename, collect_libs
import os


required_conan_version = ">=2.0"


class MimallocConan(ConanFile):
    name = "mimalloc"
    version = "2.1.2"
    python_requires = "aleya-conan-base/1.3.0@aleya/public"
    python_requires_extend = "aleya-conan-base.AleyaCmakeBase"
    ignore_cpp_standard = True

    exports_sources = "source/*"

    options = {
        "shared": [False, True],
        "fPIC": [False, True],
        "full_debug": [False, True],  # enable full debugging (slow!)
        "xmalloc": [False, True],     # abort on allocation failure
        "sanitizer": [False, True],   # address sanitizer
        "etw": [False, True],         # windows event tracing
        "secure": [False, True]       # enable security (guard pages, allocation randomization, etc..)
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "full_debug": False,
        "xmalloc": True,
        "sanitizer": False,
        "etw": False,
        "secure": False
    }

    def config_options(self):
        super().config_options()

        # Windows event tracing is only available on Windows
        # ... who would've thought?
        if self.settings.os != "Windows":
            self.options.rm_safe("etw")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ''
        tc.variables["MI_SECURE"] = self.options.get_safe("secure", False)
        tc.variables["MI_DEBUG_FULL"] = self.options.get_safe("full_debug", False)
        tc.variables["MI_OVERRIDE"] = False
        tc.variables["MI_XMALLOC"] = self.options.get_safe("xmalloc", False)
        tc.variables["MI_TRACK_ASAN"] = self.options.get_safe("sanitizer", False)
        tc.variables["MI_TRACK_ETW"] = self.options.get_safe("etw", False)
        tc.variables["MI_USE_CXX"] = False
        tc.variables["MI_SEE_ASM"] = False
        tc.variables["MI_WIN_REDIRECT"] = False
        tc.variables["MI_BUILD_SHARED"] = self.options.shared
        tc.variables["MI_BUILD_STATIC"] = not self.options.shared
        tc.variables["MI_BUILD_OBJECT"] = False
        tc.variables["MI_BUILD_TESTS"] = False
        tc.variables["MI_SKIP_COLLECT_ON_EXIT"] = False
        tc.generate()

    def package(self):
        super().package()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        versioned_dirname = "mimalloc-2.1"

        rename(self,
            os.path.join(self.package_folder, "include", versioned_dirname),
            os.path.join(self.package_folder, "include", "mimalloc"))

        copy(self,
            "*.lib",
            os.path.join(self.package_folder, "lib", versioned_dirname),
            os.path.join(self.package_folder, "lib"),
            keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "lib", versioned_dirname))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "mimalloc")
        self.cpp_info.set_property("cmake_target_name", "mimalloc::mimalloc")
        self.cpp_info.set_property("pkg_config_name", "mimalloc")

        self.cpp_info.libs = collect_libs(self)
