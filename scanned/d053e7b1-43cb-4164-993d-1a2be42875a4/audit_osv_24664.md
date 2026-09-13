# [M] NetHack Call command buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2023-24809
Aliases: GHSA-2cqv-5w4v-mgch
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2023-24809
Type: osv

## Details
NetHack is a single player dungeon exploration game. Starting with version 3.6.2 and prior to version 3.6.7, illegal input to the "C" (call) command can cause a buffer overflow and crash the NetHack process. This vulnerability may be a security issue for systems that have NetHack installed suid/sgid and for shared systems. For all systems, it may result in a process crash. This issue is resolved in NetHack 3.6.7. There are no known workarounds.

## References
- https://nethack.org/security/CVE-2023-24809.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24809.json
- https://github.com/NetHack/NetHack/security/advisories/GHSA-2cqv-5w4v-mgch
- https://nvd.nist.gov/vuln/detail/CVE-2023-24809
