# [H] Rsync version 3.4.2 and prior contain an integer overflow vulnerability in the compressed-token...

## Summary
Severity: High
Advisory: JLSEC-2026-629
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-629
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
Rsync version 3.4.2 and prior contain an integer overflow vulnerability in the compressed-token decoder where a 32-bit signed counter is not checked for overflow, allowing a malicious sender to trigger an overflow that causes the receiver process to read and return data from outside the intended buffer bounds. Attackers can exploit this vulnerability to disclose process memory contents including environment variables, passwords, heap and stack data, and library memory pointers, significantly reducing ASLR effectiveness and facilitating further exploitation.

## References
- https://access.redhat.com/errata/RHSA-2026:26332
- https://access.redhat.com/errata/RHSA-2026:26408
- https://access.redhat.com/errata/RHSA-2026:26410
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/security/cve/CVE-2026-43618
- https://bugzilla.redhat.com/show_bug.cgi?id=2469054
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-g37v-g3gj-pmwq
- https://github.com/advisories/GHSA-88m5-cm5m-2596
- https://nvd.nist.gov/vuln/detail/CVE-2026-43618
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43618.json
- https://www.vulncheck.com/advisories/rsync-integer-overflow-information-disclosure
