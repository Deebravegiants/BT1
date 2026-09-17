# [M] CVE-2021-24031

## Summary
Severity: Medium
Advisory: CVE-2021-24031
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2021-24031
Type: osv

## Details
In the Zstandard command-line utility prior to v1.4.1, output files were created with default permissions. Correct file permissions (matching the input) would only be set at completion time. Output files could therefore be readable or writable to unintended parties.

## References
- https://www.facebook.com/security/advisories/cve-2021-24031
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=981404
- https://github.com/facebook/zstd/issues/1630
