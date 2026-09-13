# [M] Galaxy vulnerable to Server Side Request Forgery during data imports

## Summary
Severity: Medium
Advisory: CVE-2023-42812
Aliases: GHSA-vf5q-r8p9-35xh
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-09-22
Source: https://osv.dev/vulnerability/CVE-2023-42812
Type: osv

## Details
Galaxy is an open-source platform for FAIR data analysis. Prior to version 22.05, Galaxy is vulnerable to server-side request forgery, which allows a malicious to issue arbitrary HTTP/HTTPS requests from the application server to internal hosts and read their responses. Version 22.05 contains a patch for this issue.

## References
- https://github.com/galaxyproject/galaxy/blob/06d56c859713b74f1c2e35da1c2fcbbf0a965645/lib/galaxy/files/uris.py
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42812.json
- https://github.com/galaxyproject/galaxy/security/advisories/GHSA-vf5q-r8p9-35xh
- https://nvd.nist.gov/vuln/detail/CVE-2023-42812
