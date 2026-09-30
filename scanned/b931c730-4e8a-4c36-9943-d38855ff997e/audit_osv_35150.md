# [C] xrdp improperly checks bounds of domain string length, which leads to Stack-based Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2025-68670
Aliases: GHSA-rwvg-gp87-gh6f
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-68670
Type: osv

## Details
xrdp is an open source RDP server. xrdp before v0.10.5 contains an unauthenticated stack-based buffer overflow vulnerability. The issue stems from improper bounds checking when processing user domain information during the connection sequence. If exploited, the vulnerability could allow remote attackers to execute arbitrary code on the target system. The vulnerability allows an attacker to overwrite the stack buffer and the return address, which could theoretically be used to redirect the execution flow. The impact of this vulnerability is lessened if a compiler flag has been used to build the xrdp executable with stack canary protection. If this is the case, a second vulnerability would need to be used to leak the stack canary value. Upgrade to version 0.10.5 to receive a patch. Additionally, do not rely on stack canary protection on production systems.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.5
- https://lists.debian.org/debian-lts-announce/2026/02/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68670.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-rwvg-gp87-gh6f
- https://nvd.nist.gov/vuln/detail/CVE-2025-68670
- https://github.com/neutrinolabs/xrdp/commit/488c8c7d4d189514a366cd8301b6e816c5218ffa
