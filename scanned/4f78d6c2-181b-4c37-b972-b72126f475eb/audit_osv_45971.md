# [H] JLSEC-2026-530

## Summary
Severity: High
Advisory: JLSEC-2026-530
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-530
Type: osv

## Affected
- Julia: `Raylib_jll` — affected >=0 <6.0.0+0

## Details
A vulnerability was determined in raysan5 raylib up to 909f040. Affected by this vulnerability is the function GenImageFontAtlas of the file `src/rtext.c`. Executing a manipulation can lead to heap-based buffer overflow. The attack can only be executed locally. The exploit has been publicly disclosed and may be utilized. This patch is called 5a3391fdce046bc5473e52afbd835dd2dc127146. Applying a patch is advised to resolve this issue.

## References
- https://github.com/oneafter/1224/blob/main/hbf2
- https://github.com/raysan5/raylib/
- https://github.com/raysan5/raylib/commit/5a3391fdce046bc5473e52afbd835dd2dc127146
- https://github.com/raysan5/raylib/issues/5433
- https://github.com/raysan5/raylib/pull/5450
- https://vuldb.com/?ctiid.341705
- https://vuldb.com/?id.341705
- https://vuldb.com/?submit.733341
- https://vuldb.com/?submit.733342
