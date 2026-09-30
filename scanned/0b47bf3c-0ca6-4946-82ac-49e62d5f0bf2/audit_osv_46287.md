# [H] ImageMagick affected by divide-by-zero in ThumbnailImage via montage -geometry ":" leads to crash

## Summary
Severity: High
Advisory: JLSEC-2026-923
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-923
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2004+0

## Details
## Summary

Passing a geometry string containing only a colon (":") to montage -geometry leads GetGeometry() to set width/height to 0. Later, ThumbnailImage() divides by these zero dimensions, triggering a crash (SIGFPE/abort), resulting in a denial of service.

## Details

**Root Cause**

 1. `montage -geometry ":" ...` reaches `MagickCore/geometry.c:GetGeometry().`
 2. `StringToDouble/InterpretLocaleValue` parses `":"` as `0.0;` then:
    https://github.com/ImageMagick/ImageMagick/blob/0ba1b587be17543b664f7ad538e9e51e0da59d17/MagickCore/geometry.c#L355
    `WidthValue` (and/or `HeightValue)` is set with a zero dimension.
 3. In MagickCore/resize.c:ThumbnailImage(), the code computes:
    https://github.com/ImageMagick/ImageMagick/blob/0ba1b587be17543b664f7ad538e9e51e0da59d17/MagickCore/resize.c#L4625-L4629
    causing a division by zero and immediate crash.

The issue is trivially triggerable without external input files (e.g., using `xc:white`).

### Reproduction

Environment

```
Version: ImageMagick 7.1.2-1 (Beta) Q16-HDRI x86_64 0ba1b587b:20250812 https://imagemagick.org
Features: Cipher DPC HDRI
Delegates (built-in): bzlib fontconfig freetype jbig jng jpeg lcms lzma pangocairo png tiff x xml zlib
Compiler: clang (14.0.0)
OS/Arch: Linux x86_64
```

Steps

```
./bin/magick montage -geometry : xc:white null:
```

Observed result

```
IOT instruction (core dumped)
# (Environment-dependent: SIGFPE/abort may be observed.)
```

## PoC

No external file required; the pseudo image xc:white suffices:

```
./bin/magick montage -geometry : xc:white null:
```

## Impact

  - **Denial of Service:** A divide-by-zero in `ThumbnailImage()` causes immediate abnormal termination (e.g., SIGFPE/abort), crashing the ImageMagick process.

## Suggested fix

Defensively reject zero dimensions early in `ThumbnailImage()`:

```c
if ((columns == 0) || (rows == 0)) {
  (void) ThrowMagickException(exception, GetMagickModule(), OptionError,
    "InvalidGeometry", "thumbnail requires non-zero dimensions: %.20gx%.20g",
    (double) columns, (double) rows);
  return (Image *) NULL;
}
```

Additionally, consider tightening validation in `GetGeometry()` so that colon-only (and similar malformed) inputs do not yield `WidthValue/HeightValue` with zero, or are rejected outright. Variants like `"x:"` or `":x"` may also need explicit handling (maintainer confirmation requested).

## Credits

### Team Daemon Fuzz Hunters

**Bug Hunting Master Program, HSpace/Findthegap**
<br>

**Woojin Park**
@jin-156
[1203kids@gmail.com](mailto:1203kids@gmail.com)

**Hojun Lee**
@leehohojune
[leehojune@korea.ac.kr](mailto:leehojune@korea.ac.kr)

**Youngin Won**
@amethyst0225
[youngin04@korea.ac.kr](mailto:youngin04@korea.ac.kr)

**Siyeon Han**
@hanbunny
[kokosyeon@gmail.com](mailto:kokosyeon@gmail.com)

## References
- https://github.com/ImageMagick/ImageMagick/blob/0ba1b587be17543b664f7ad538e9e51e0da59d17/MagickCore/geometry.c#L355
- https://github.com/ImageMagick/ImageMagick/blob/0ba1b587be17543b664f7ad538e9e51e0da59d17/MagickCore/resize.c#L4625-L4629
- https://github.com/ImageMagick/ImageMagick/commit/5f0bcf986b8b5e90567750d31a37af502b73f2af
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-fh55-q5pj-pxgw
- https://github.com/advisories/GHSA-fh55-q5pj-pxgw
- https://github.com/dlemstra/Magick.NET/releases/tag/14.8.1
- https://lists.debian.org/debian-lts-announce/2025/09/msg00012.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-55212
