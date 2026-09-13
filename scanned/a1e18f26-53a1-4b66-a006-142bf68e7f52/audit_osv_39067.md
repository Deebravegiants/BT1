# [H] Rsync < 3.4.3 Integer Overflow Information Disclosure

## Summary
Severity: High
Advisory: CVE-2026-43618
Aliases: GHSA-g37v-g3gj-pmwq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-43618
Type: osv

## Details
Rsync version 3.4.2 and prior contain an integer overflow vulnerability in the compressed-token decoder where a 32-bit signed counter is not checked for overflow, allowing a malicious sender to trigger an overflow that causes the receiver process to read and return data from outside the intended buffer bounds. Attackers can exploit this vulnerability to disclose process memory contents including environment variables, passwords, heap and stack data, and library memory pointers, significantly reducing ASLR effectiveness and facilitating further exploitation.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43618.json
- https://access.redhat.com/errata/RHSA-2026:26332
- https://access.redhat.com/errata/RHSA-2026:26408
- https://access.redhat.com/errata/RHSA-2026:26410
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/security/cve/CVE-2026-43618
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43618.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-g37v-g3gj-pmwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-43618
- https://www.vulncheck.com/advisories/rsync-integer-overflow-information-disclosure
- https://bugzilla.redhat.com/show_bug.cgi?id=2469054
- https://github.com/RsyncProject/rsync
