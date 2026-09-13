# [C] CVE-2024-38428

## Summary
Severity: Critical
Advisory: CVE-2024-38428
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-06-16
Source: https://osv.dev/vulnerability/CVE-2024-38428
Type: osv

## Details
url.c in GNU Wget through 1.24.5 mishandles semicolons in the userinfo subcomponent of a URI, and thus there may be insecure behavior in which data that was supposed to be in the userinfo subcomponent is misinterpreted to be part of the host subcomponent.

## References
- https://git.savannah.gnu.org/cgit/wget.git/commit/?id=ed0c7c7e0e8f7298352646b2fd6e06a11e242ace
- https://lists.debian.org/debian-lts-announce/2025/04/msg00029.html
- https://lists.gnu.org/archive/html/bug-wget/2024-06/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38428.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38428
- https://security.netapp.com/advisory/ntap-20241115-0005/
