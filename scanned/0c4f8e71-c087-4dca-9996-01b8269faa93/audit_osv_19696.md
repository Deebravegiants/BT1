# [M] CVE-2021-24032

## Summary
Severity: Medium
Advisory: CVE-2021-24032
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2021-24032
Type: osv

## Details
Beginning in v1.4.1 and prior to v1.4.9, due to an incomplete fix for CVE-2021-24031, the Zstandard command-line utility created output files with default permissions and restricted those permissions immediately afterwards. Output files could therefore momentarily be readable or writable to unintended parties.

## References
- https://www.facebook.com/security/advisories/cve-2021-24032
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=982519
- https://github.com/facebook/zstd/issues/2491
