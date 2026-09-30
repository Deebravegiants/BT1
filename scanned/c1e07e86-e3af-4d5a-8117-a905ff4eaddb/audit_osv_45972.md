# [H] JLSEC-2026-531

## Summary
Severity: High
Advisory: JLSEC-2026-531
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-531
Type: osv

## Affected
- Julia: `Raylib_jll` — affected >=0 <6.0.0+0

## Details
A vulnerability was identified in raysan5 raylib up to 909f040. Affected by this issue is the function LoadFontData of the file `src/rtext.c`. The manipulation leads to integer overflow. The attack can only be performed from a local environment. The exploit is publicly available and might be used. The identifier of the patch is 5a3391fdce046bc5473e52afbd835dd2dc127146. It is suggested to install a patch to address this issue.

## References
- https://github.com/oneafter/1224/blob/main/segv1
- https://github.com/raysan5/raylib/
- https://github.com/raysan5/raylib/commit/5a3391fdce046bc5473e52afbd835dd2dc127146
- https://github.com/raysan5/raylib/issues/5436
- https://github.com/raysan5/raylib/pull/5450
- https://vuldb.com/?ctiid.341706
- https://vuldb.com/?id.341706
- https://vuldb.com/?submit.733343
