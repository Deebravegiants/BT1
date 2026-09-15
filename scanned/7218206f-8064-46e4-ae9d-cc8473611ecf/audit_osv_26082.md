# [H] An unrestricted file upload vulnerability in traccar leads to RCE

## Summary
Severity: High
Advisory: CVE-2023-50729
Aliases: GHSA-pqf7-8g85-vx2q
CVSS: 8.4 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-01-15
Source: https://osv.dev/vulnerability/CVE-2023-50729
Type: osv

## Details
Traccar is an open source GPS tracking system. Prior to 5.11, Traccar is affected by an unrestricted file upload vulnerability in File feature allows attackers to execute arbitrary code on the server. This vulnerability is more prevalent because Traccar is recommended to run web servers as root user. It is also more dangerous because it can write or overwrite files in arbitrary locations.  Version 5.11 was published to fix this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50729.json
- https://github.com/traccar/traccar/security/advisories/GHSA-pqf7-8g85-vx2q
- https://nvd.nist.gov/vuln/detail/CVE-2023-50729
