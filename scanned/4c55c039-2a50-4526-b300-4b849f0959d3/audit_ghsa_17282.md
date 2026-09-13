# [M] ImageMagick's failure to limit the depth of SVG file reads caused a DoS attack

## Summary
Severity: Medium
Advisory: GHSA-p27m-hp98-6637
CVE: CVE-2025-68618
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-p27m-hp98-6637
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.1

## Details
### Summary

Using Magick to read a malicious SVG file resulted in a DoS attack.

### Details

bt obtained using gdb:

```
#4 0x0000555555794c9c in ResizeMagickMemory (memory=0x7fffee203800, size=391344) at MagickCore/memory.c:1443
#5 0x0000555555794e5a in ResizeQuantumMemory (memory=0x7fffee203800, count=48918, quantum=8) 
at MagickCore/memory.c:1508
#6 0x0000555555acc8ed in SVGStartElement (context=0x517000000080, name=0x5190000055e3 "g", attributes=0x0) 
at coders/svg.c:1254
#7 0x00007ffff6799b1c in xmlParseStartTag () at /lib/x86_64-linux-gnu/libxml2.so.2
#8 0x00007ffff68c7bb8 in () at /lib/x86_64-linux-gnu/libxml2.so.2
#9 0x00007ffff67a03f1 in xmlParseChunk () at /lib/x86_64-linux-gnu/libxml2.so.2
```

This is related to the SVGStartElement and ResizeQuantumMemory functions.

### PoC

1. Generate an SVG file

2. Read this file using Magick:

```
./magick /data/ylwang/Tools/LargeScan/targets/ImageMagick/test++/1.svg null
```

3. Causes a DoS Attack

My server has a large amount of memory, causing a stack overflow to take a long time. I'll use the Windows release version as an example:

``` 
PS C:\Program Files\ImageMagick-7.1.2-Q8> .\magick.exe -ping 1.svg null:
PS C:\Program Files\ImageMagick-7.1.2-Q8> echo $LASTEXITCODE
-1073741571
```

The error code -1073741571 indicates a crash due to a stack overflow.

### Impact

This is a DoS vulnerability and all applications using Magick to parse SVG files are affected.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-p27m-hp98-6637
- https://nvd.nist.gov/vuln/detail/CVE-2025-68618
- https://github.com/ImageMagick/ImageMagick/commit/6f431d445f3ddd609c004a1dde617b0a73e60beb
- https://github.com/ImageMagick/ImageMagick
