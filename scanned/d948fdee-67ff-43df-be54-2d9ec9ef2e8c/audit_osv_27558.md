# [M] Thruk Incorrect limitation of a pathname to a restricted directory (Path Traversal) (CWE-22)

## Summary
Severity: Medium
Advisory: CVE-2024-23822
Aliases: GHSA-4mrh-mx7x-rqjx
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2024-23822
Type: osv

## Details
Thruk is a multibackend monitoring webinterface.  Prior to 3.12, the Thruk web monitoring application presents a vulnerability in a file upload form that allows a threat actor to arbitrarily upload files to the server to any path they desire and have permissions for. This vulnerability is known as Path Traversal or Directory Traversal. Version 3.12 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23822.json
- https://github.com/sni/Thruk/security/advisories/GHSA-4mrh-mx7x-rqjx
- https://nvd.nist.gov/vuln/detail/CVE-2024-23822
- https://github.com/sni/Thruk/commit/1aa9597cdf2722a69651124f68cbb449be12cc39
