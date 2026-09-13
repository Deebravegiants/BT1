# [M] JLSEC-2026-18

## Summary
Severity: Medium
Advisory: JLSEC-2026-18
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/JLSEC-2026-18
Type: osv

## Affected
- Julia: `patch_jll` — affected >=0 <2.8.0+0

## Details
GNU patch through 2.7.6 contains a free(`p_line`[`p_end`]) Double Free vulnerability in the function `another_hunk` in pch.c that can cause a denial of service via a crafted patch file. NOTE: this issue exists because of an incomplete fix for CVE-2018-6952.

## References
- https://savannah.gnu.org/bugs/index.php?56683
