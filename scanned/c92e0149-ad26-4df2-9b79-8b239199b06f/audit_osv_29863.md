# [M] Dozzle uses unsafe hash for passwords

## Summary
Severity: Medium
Advisory: CVE-2024-47182
Aliases: GHSA-w7qr-q9fh-fj35, GO-2024-3163
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-47182
Type: osv

## Details
Dozzle is a realtime log viewer for docker containers. Before version 8.5.3, the app uses sha-256 as the hash for passwords, which leaves users susceptible to rainbow table attacks. The app switches to bcrypt, a more appropriate hash for passwords, in version 8.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47182.json
- https://github.com/amir20/dozzle/security/advisories/GHSA-w7qr-q9fh-fj35
- https://nvd.nist.gov/vuln/detail/CVE-2024-47182
- https://github.com/amir20/dozzle/commit/de79f03aa3dbe5bb1e154a7e8d3dccbd229f3ea3
