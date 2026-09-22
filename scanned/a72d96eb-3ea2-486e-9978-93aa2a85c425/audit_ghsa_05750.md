# [M] ImageMagick has a Memory Leak in LoadOpenCLDeviceBenchmark() when parsing malformed XML

## Summary
Severity: Medium
Advisory: GHSA-qp59-x883-77qv
CWE: CWE-763
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-qp59-x883-77qv
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.2

## Details
### Summary

A memory leak vulnerability exists in the `LoadOpenCLDeviceBenchmark()` function in `MagickCore/opencl.c`. When parsing a malformed OpenCL device profile XML file that contains `<device` elements without proper `/>` closing tags, the function fails to release allocated memory for string members (`platform_name`, `vendor_name`, `name`, `version`), leading to memory leaks that could result in resource exhaustion.

**Affected Version**: ImageMagick 7.1.2-12 and possibly earlier versions

---

### Details

The vulnerability is located in `MagickCore/opencl.c`, function `LoadOpenCLDeviceBenchmark()` (lines 754-911).

**Root Cause Analysis:**

1. When a `<device` tag is encountered, a `MagickCLDeviceBenchmark` structure is allocated (line 807-812)
2. String attributes (`platform`, `vendor`, `name`, `version`) are allocated via `ConstantString()` (lines 878, 885, 898, 900)
3. These strings are **only freed** when a `/>` closing tag is encountered (lines 840-849)
4. At function exit (lines 908-910), only the `device_benchmark` structure is freed, but **its member variables are not freed** if `/>` was never parsed

**Vulnerable Code (lines 908-910):**

```c
token=(char *) RelinquishMagickMemory(token);
device_benchmark=(MagickCLDeviceBenchmark *) RelinquishMagickMemory(
  device_benchmark);  // BUG: members (platform_name, vendor_name, name, version) not freed!
```

**Correct cleanup (only executed when `/>` is found, lines 840-849):**

```c
device_benchmark->platform_name=(char *) RelinquishMagickMemory(device_benchmark->platform_name);
device_benchmark->vendor_name=(char *) RelinquishMagickMemory(device_benchmark->vendor_name);
device_benchmark->name=(char *) RelinquishMagickMemory(device_benchmark->name);
device_benchmark->version=(char *) RelinquishMagickMemory(device_benchmark->version);
device_benchmark=(MagickCLDeviceBenchmark *) RelinquishMagickMemory(device_benchmark);
```

---

### PoC

**Environment:**
- OS: Ubuntu 22.04.5 LTS (Linux 6.8.0-87-generic x86_64)
- Compiler: GCC 11.4.0
- ImageMagick: 7.1.2-13 (commit `a52c1b402be08ef8ae193f28ac5b2e120f2fa26f`)

**Step 1: Build ImageMagick with AddressSanitizer**

```bash
cd ImageMagick
./configure \
    CFLAGS="-g -O0 -fsanitize=address -fno-omit-frame-pointer" \
    CXXFLAGS="-g -O0 -fsanitize=address -fno-omit-frame-pointer" \
    LDFLAGS="-fsanitize=address" \
    --disable-openmp
make -j$(nproc)
```

**Step 2: Create malformed XML file**

**Step 3: Place file in OpenCL cache directory**

```bash
mkdir -p ~/.cache/ImageMagick
cp malformed_opencl_profile.xml ~/.cache/ImageMagick/ImagemagickOpenCLDeviceProfile.xml
```

**Step 4: Run ImageMagick with leak detection**

```bash
export ASAN_OPTIONS="detect_leaks=1:symbolize=1"
./utilities/magick -size 100x100 xc:red output.png
```

**ASAN Output:**

```
=================================================================
==2543490==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 96 byte(s) in 2 object(s) allocated from:
    #0 ... in AcquireMagickMemory MagickCore/memory.c:536
    #1 ... in LoadOpenCLDeviceBenchmark MagickCore/opencl.c:807

Direct leak of 16 byte(s) in 1 object(s) allocated from:
    #0 ... in ConstantString MagickCore/string.c:692
    #1 ... in LoadOpenCLDeviceBenchmark MagickCore/opencl.c:878  ← name

Direct leak of 14 byte(s) in 1 object(s) allocated from:
    #0 ... in ConstantString MagickCore/string.c:692
    #1 ... in LoadOpenCLDeviceBenchmark MagickCore/opencl.c:885  ← platform_name

Direct leak of 14 byte(s) in 1 object(s) allocated from:
    #0 ... in ConstantString MagickCore/string.c:692
    #1 ... in LoadOpenCLDeviceBenchmark MagickCore/opencl.c:898  ← vendor_name

Direct leak of 15 byte(s) in 1 object(s) allocated from:
    #0 ... in ConstantString MagickCore/string.c:692
    #1 ... in LoadOpenCLDeviceBenchmark MagickCore/opencl.c:900  ← version

SUMMARY: AddressSanitizer: 203 byte(s) leaked in 18 allocation(s).
```

---

### Impact

**Vulnerability Type:** CWE-401 (Missing Release of Memory after Effective Lifetime)

**Severity:** Low

**Who is impacted:**
- Users who have OpenCL enabled in ImageMagick
- Systems where an attacker can place or modify files in the OpenCL cache directory (`~/.cache/ImageMagick/`)
- Long-running ImageMagick processes or services that repeatedly initialize OpenCL

**Potential consequences:**
- Memory exhaustion over time if the malformed configuration is repeatedly loaded
- Denial of Service (DoS) in resource-constrained environments

**Attack Vector:** Local - requires write access to the user's OpenCL cache directory

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qp59-x883-77qv
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.2
