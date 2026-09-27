# [M] JLSEC-2026-1298

## Summary
Severity: Medium
Advisory: JLSEC-2026-1298
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1298
Type: osv

## Affected
- Julia: `libxls_jll` — affected >=1.6.2+0

## Details
Buffer Overflow vulnerability in libxlsv.1.6.2 allows a remote attacker to execute arbitrary code and cause a denial of service via a crafted XLS file to the `transcode_latin1_to_utf8` function in xlstool.c:296.

## References
- https://github.com/libxls/libxls/issues/124
- https://github.com/libxls/libxls/issues/124
