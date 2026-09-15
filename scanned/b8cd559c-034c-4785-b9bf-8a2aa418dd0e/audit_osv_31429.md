# [M] missing SFTP host verification with wolfSSH

## Summary
Severity: Medium
Advisory: CVE-2025-10966
Aliases: CURL-CVE-2025-10966
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-10966
Type: osv

## Details
curl's code for managing SSH connections when SFTP was done using the wolfSSH
powered backend was flawed and missed host verification mechanisms.

This prevents curl from detecting MITM attackers and more.

## References
- http://www.openwall.com/lists/oss-security/2025/11/05/2
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://curl.se/docs/CVE-2025-10966.html
- https://curl.se/docs/CVE-2025-10966.json
- https://hackerone.com/reports/3355218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10966.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10966
