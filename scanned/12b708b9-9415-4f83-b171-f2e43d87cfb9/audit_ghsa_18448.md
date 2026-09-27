# [H] ImageMagick has XMP profile write that triggers hang due to unbounded loop

## Summary
Severity: High
Advisory: GHSA-vmhh-8rxq-fp9g
CVE: CVE-2025-53015
CWE: CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-vmhh-8rxq-fp9g
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.7.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.7.0

## Details
### Summary
Infinite lines occur when writing during a specific XMP file conversion command
### Details
```
#0  GetXmpNumeratorAndDenominator (denominator=<optimized out>, numerator=<optimized out>, value=<optimized out>) at MagickCore/profile.c:2578
#1  GetXmpNumeratorAndDenominator (denominator=<synthetic pointer>, numerator=<synthetic pointer>, value=720000000000000) at MagickCore/profile.c:2564
#2  SyncXmpProfile (image=image@entry=0x555555bb9ea0, profile=0x555555b9d020) at MagickCore/profile.c:2605
#3  0x00005555555db5cf in SyncImageProfiles (image=image@entry=0x555555bb9ea0) at MagickCore/profile.c:2651
#4  0x0000555555798d4f in WriteImage (image_info=image_info@entry=0x555555bc2050, image=image@entry=0x555555bb9ea0, exception=exception@entry=0x555555b7bea0) at MagickCore/constitute.c:1288
#5  0x0000555555799862 in WriteImages (image_info=image_info@entry=0x555555bb69c0, images=<optimized out>, images@entry=0x555555bb9ea0, filename=<optimized out>, exception=0x555555b7bea0) at MagickCore/constitute.c:1575
#6  0x00005555559650c4 in CLINoImageOperator (cli_wand=cli_wand@entry=0x555555b85790, option=option@entry=0x5555559beebe "-write", arg1n=arg1n@entry=0x7fffffffe2c7 "a.mng", arg2n=arg2n@entry=0x0) at MagickWand/operation.c:4993
#7  0x0000555555974579 in CLIOption (cli_wand=cli_wand@entry=0x555555b85790, option=option@entry=0x5555559beebe "-write") at MagickWand/operation.c:5473
#8  0x00005555559224aa in ProcessCommandOptions (cli_wand=cli_wand@entry=0x555555b85790, argc=argc@entry=3, argv=argv@entry=0x7fffffffdfa8, index=index@entry=1) at MagickWand/magick-cli.c:758
#9  0x000055555592276d in MagickImageCommand (image_info=image_info@entry=0x555555b824a0, argc=argc@entry=3, argv=argv@entry=0x7fffffffdfa8, metadata=metadata@entry=0x7fffffffbc10, exception=exception@entry=0x555555b7bea0) at MagickWand/magick-cli.c:1392
#10 0x00005555559216a0 in MagickCommandGenesis (image_info=image_info@entry=0x555555b824a0, command=command@entry=0x555555922640 <MagickImageCommand>, argc=argc@entry=3, argv=argv@entry=0x7fffffffdfa8, metadata=0x0, exception=exception@entry=0x555555b7bea0) at MagickWand/magick-cli.c:177
#11 0x000055555559f76b in MagickMain (argc=3, argv=0x7fffffffdfa8) at utilities/magick.c:162
#12 0x00007ffff700fd90 in __libc_start_call_main (main=main@entry=0x55555559aec0 <main>, argc=argc@entry=3, argv=argv@entry=0x7fffffffdfa8) at ../sysdeps/nptl/libc_start_call_main.h:58
#13 0x00007ffff700fe40 in __libc_start_main_impl (main=0x55555559aec0 <main>, argc=3, argv=0x7fffffffdfa8, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7fffffffdf98) at ../csu/libc-start.c:392
#14 0x000055555559f535 in _start ()
```
```
static void GetXmpNumeratorAndDenominator(double value,
  unsigned long *numerator,unsigned long *denominator)
{
  double
    df;

  *numerator=0;
  *denominator=1;
  if (value <= MagickEpsilon)
    return;
  *numerator=1;
  df=1.0;
  while(fabs(df - value) > MagickEpsilon)
  {
    if (df < value)
      (*numerator)++;
    else
      {
        (*denominator)++;
        *numerator=(unsigned long) (value*(*denominator));
      }
    df=*numerator/(double)*denominator;
  }
}
```
In this code, the loop `while(fabs(df - value) > MagickEpsilon)` keeps repeating endlessly.

### PoC
`magick hang a.mng`
https://drive.google.com/file/d/1iegkwlTjqnJTtM4XkiheYsjKsC6pxtId/view?usp=sharing

### Impact
XMP profile write triggers hang due to unbounded loop


### credits
**Team Pay1oad DVE** 

**Reporter** :  **Shinyoung Won** (with contributions from **WooJin Park, DongHa Lee, JungWoo Park, Woojin Jeon, Juwon Chae**, **Kyusang Han, JaeHun Gou**)

**yosimich(@yosiimich**) **Shinyoung Won** of SSA Lab

e-mail : [yosimich123@gmail.com]

**Woojin Jeon**

Gtihub : brainoverflow

e-mail : [root@brainoverflow.kr]

**WooJin Park**

GitHub : jin-156

e-mail : [1203kids@gmail.com]

**Who4mI(@GAP-dev) Lee DongHa of SSA Lab**

Github: GAP-dev

e-mail : [ceo@zeropointer.co.kr]

**JungWoo Park**

Github : JungWooJJING

e-mail : [cuby5577@gmail.com]

**Juwon Chae** 

Github : I_mho

e-mail : [wndnjs4698@naver.com]

**Kyusang Han**

Github : T1deSEC

e-mail : [hksjoe0081@gmail.com]

**JaeHun Gou**

Github : P2GONE

e-mail : [charly20@naver.com]

### Commits
Fixed in: https://github.com/ImageMagick/ImageMagick/commit/229fa96a988a21d78318bbca61245a6ed1ee33a0 and https://github.com/ImageMagick/ImageMagick/commit/38631605e6ab744548a561797472cf8648bcfe26

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-vmhh-8rxq-fp9g
- https://nvd.nist.gov/vuln/detail/CVE-2025-53015
- https://github.com/ImageMagick/ImageMagick/commit/229fa96a988a21d78318bbca61245a6ed1ee33a0
- https://github.com/ImageMagick/ImageMagick/commit/38631605e6ab744548a561797472cf8648bcfe26
- https://drive.google.com/file/d/1iegkwlTjqnJTtM4XkiheYsjKsC6pxtId/view?usp=sharing
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.7.0
