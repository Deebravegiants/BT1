# [H] Cryptomator's MSI installer allows local privilege escalation

## Summary
Severity: High
Advisory: CVE-2023-37907
Aliases: GHSA-9c9p-c3mg-hpjq
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-37907
Type: osv

## Details
Cryptomator is data encryption software for users who store their files in the cloud. Prior to version 1.9.2, the MSI installer provided on the homepage allows local privilege escalation (LPE) for low privileged users, if already installed. The problem occurs as the repair function of the MSI spawns two administrative CMDs. A simple LPE is possible via a breakout. Version 1.9.2 fixes this issue.

## References
- https://github.com/cryptomator/cryptomator/releases/tag/1.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37907.json
- https://github.com/cryptomator/cryptomator/security/advisories/GHSA-9c9p-c3mg-hpjq
- https://nvd.nist.gov/vuln/detail/CVE-2023-37907
- https://github.com/cryptomator/cryptomator/commit/b48ebd524b1626bf12ac98e35a7670b868fa208c
