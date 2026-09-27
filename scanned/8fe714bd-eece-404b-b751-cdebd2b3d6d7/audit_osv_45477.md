# [M] Beginning in v1.4.1 and prior to v1.4.9, due to an incomplete fix for CVE-2021-24031, the Zstandard...

## Summary
Severity: Medium
Advisory: JLSEC-2026-121
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/JLSEC-2026-121
Type: osv

## Affected
- Julia: `Zstd_jll` — affected >=0 <1.5.0+0

## Details
Beginning in v1.4.1 and prior to v1.4.9, due to an incomplete fix for CVE-2021-24031, the Zstandard command-line utility created output files with default permissions and restricted those permissions immediately afterwards. Output files could therefore momentarily be readable or writable to unintended parties.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=982519
- https://github.com/advisories/GHSA-ffqj-7pgc-cmj5
- https://github.com/facebook/zstd/issues/2491
- https://nvd.nist.gov/vuln/detail/CVE-2021-24032
- https://www.facebook.com/security/advisories/cve-2021-24032
