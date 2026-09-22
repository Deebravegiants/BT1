# [M] ImageMagick has a NULL pointer dereference in MSL parser via <comment> tag before image load

## Summary
Severity: Medium
Advisory: GHSA-5vx3-wx4q-6cj8
CVE: CVE-2026-23952
CWE: CWE-476
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-5vx3-wx4q-6cj8
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
## Summary

NULL pointer dereference in MSL (Magick Scripting Language) parser when processing `<comment>` tag before any image is loaded.

## Version

- ImageMagick 7.x (tested on current main branch)
- Commit: HEAD

## Steps to Reproduce

### Method 1: Using ImageMagick directly

```bash
magick MSL:poc.msl out.png
```

### Method 2: Using OSS-Fuzz reproduce

```bash
python3 infra/helper.py build_fuzzers imagemagick
python3 infra/helper.py reproduce imagemagick msl_fuzzer poc.msl
```

Or run the fuzzer directly:
```bash
./msl_fuzzer poc.msl
```

## Expected Behavior

ImageMagick should handle the malformed MSL gracefully and return an error message.

## Actual Behavior

```
convert: MagickCore/property.c:297: MagickBooleanType DeleteImageProperty(Image *, const char *): Assertion `image != (Image *) NULL' failed.
Aborted
```

## Root Cause Analysis

In `coders/msl.c:7091`, `MSLEndElement()` calls `DeleteImageProperty()` on `msl_info->image[n]` when handling the `</comment>` end tag without checking if the image is NULL:

```c
if (LocaleCompare((const char *) tag,"comment") == 0 )
  {
    (void) DeleteImageProperty(msl_info->image[n],"comment");  // No NULL check
    ...
  }
```

When `<comment>` appears before any `<read>` operation, `msl_info->image[n]` is NULL, causing the assertion failure in `DeleteImageProperty()` at `property.c:297`.

## Impact

- **DoS**: Crash via assertion failure (debug builds) or NULL pointer dereference (release builds)
- **Affected**: Any application using ImageMagick to process user-supplied MSL files

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
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-5vx3-wx4q-6cj8
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.2
