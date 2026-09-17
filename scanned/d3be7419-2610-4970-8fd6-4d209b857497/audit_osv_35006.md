# [C] CVE-2025-67418

## Summary
Severity: Critical
Advisory: CVE-2025-67418
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-67418
Type: osv

## Details
ClipBucket 5.5.2 is affected by an improper access control issue where the product is shipped or deployed with hardcoded default administrative credentials. An unauthenticated remote attacker can log in to the administrative panel using these default credentials, resulting in full administrative control of the application.

## References
- https://medium.com/@arpit03sharma2003/cve-2025-67418-when-default-credentials-become-a-remote-root-button-03be5ee4b927
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67418.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67418
