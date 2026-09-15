# [M] ImageMagick MSL: Stack overflow via infinite recursion in ProcessMSLScript

## Summary
Severity: Medium
Advisory: GHSA-9vj4-wc7r-p844
CVE: CVE-2026-23874
CWE: CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-9vj4-wc7r-p844
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
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.2

## Details
## Summary

Stack overflow via infinite recursion in MSL (Magick Scripting Language) `<write>` command when writing to MSL format.

## Version

- ImageMagick 7.x (tested on current main branch)
- Commit: HEAD
- Requires: libxml2 support (for MSL parsing)

## Steps to Reproduce

### Method 1: Using ImageMagick directly

```bash
magick MSL:recursive.msl out.png
```

### Method 2: Using OSS-Fuzz reproduce

```bash
python3 infra/helper.py build_fuzzers imagemagick
python3 infra/helper.py reproduce imagemagick msl_fuzzer recursive.msl
```

Or run the fuzzer directly:
```bash
./msl_fuzzer recursive.msl
```

## Expected Behavior

ImageMagick should handle recursive MSL references gracefully by detecting the loop and returning an error.

## Actual Behavior

Stack overflow causes process crash:

```
AddressSanitizer:DEADLYSIGNAL
==PID==ERROR: AddressSanitizer: stack-overflow
    #0 MSLStartElement /src/imagemagick/coders/msl.c:7045
    #1 xmlParseStartTag /src/libxml2/parser.c
    #2 xmlParseChunk /src/libxml2/parser.c:11273
    #3 ProcessMSLScript /src/imagemagick/coders/msl.c:7405
    #4 WriteMSLImage /src/imagemagick/coders/msl.c:7867
    #5 WriteImage /src/imagemagick/MagickCore/constitute.c:1346
    #6 MSLStartElement /src/imagemagick/coders/msl.c:7045
    ... (infinite recursion, 287+ frames)
```

## Root Cause Analysis

In `coders/msl.c`, the `<write>` command handler in `MSLStartElement()` (line ~7045) calls `WriteImage()`. When the output filename specifies MSL format (`msl:filename`), `WriteMSLImage()` is called, which parses the MSL file again via `ProcessMSLScript()`.

If the MSL file references itself (directly or indirectly), this creates an infinite recursion loop:

```
MSLStartElement() → WriteImage() → WriteMSLImage() → ProcessMSLScript()
    → xmlParseChunk() → MSLStartElement() → ... (infinite loop)
```

## Impact

- **DoS**: Guaranteed crash via stack exhaustion
- **Affected**: Any application using ImageMagick to process user-supplied MSL files

## Additional Trigger Paths

The `<read>` command can also trigger recursion:

Indirect recursion is also possible (a.msl → b.msl → a.msl).

## Fuzzer

This issue was discovered using a custom MSL fuzzer:

```cpp
#include <cstdint>
#include <Magick++/Blob.h>
#include <Magick++/Image.h>
#include "utils.cc"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
{
  if (IsInvalidSize(Size))
    return(0);
  try
  {
    const Magick::Blob blob(Data, Size);
    Magick::Image image;
    image.magick("MSL");
    image.fileName("MSL:");
    image.read(blob);
  }
  catch (Magick::Exception)
  {
  }
  return(0);
}
```

This issue was found by Team FuzzingBrain @ Texas A&M University

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-9vj4-wc7r-p844
- https://nvd.nist.gov/vuln/detail/CVE-2026-23874
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.2
