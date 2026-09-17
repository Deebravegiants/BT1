# [C] Velociraptor authenticated identity-spoofing vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-18972
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18972
Type: osv

## Details
An authenticated attacker can spoof another GUI user's identity by sending their request with the custom header \"Grpc-Metadata-USER\". This can lead to an account takeover attack from a user with low privileges to administrator.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18972/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18972
