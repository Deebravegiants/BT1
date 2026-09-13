# [C] cryptodev-linux <= 1.14 get_userbuf Use After Free LPE

## Summary
Severity: Critical
Advisory: CVE-2026-28529
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-28529
Type: osv

## Details
cryptodev-linux version 1.14 and prior contain a page reference handling flaw in the get_userbuf function of the /dev/crypto device driver that allows local users to trigger use-after-free conditions. Attackers with access to the /dev/crypto interface can repeatedly decrement reference counts of controlled pages to achieve local privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28529.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28529
- https://www.vulncheck.com/advisories/cryptodev-linux-get-userbuf-use-after-free-lpe
- https://github.com/cryptodev-linux/cryptodev-linux/pull/104
- https://github.com/cryptodev-linux/cryptodev-linux
- https://gist.github.com/n4sm/0fd2479e0c23e0fa2f192cd8fda45750
- https://nasm.re/posts/cryptodev-linux-vuln/
