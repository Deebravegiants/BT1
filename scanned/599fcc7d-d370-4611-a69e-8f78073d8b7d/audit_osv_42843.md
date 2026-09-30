# [M] INDI indiserver 2.2.4.2 Stack Buffer Overflow via XML Tag Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-71979
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71979
Type: osv

## Details
INDI (Instrument Neutral Distributed Interface) indiserver through 2.2.4.2, fixed in commit 96bbd7f, contains a stack buffer overflow vulnerability that allows unauthenticated remote attackers to crash the daemon by sending malformed XML with mismatched tags whose names exceed 1024 bytes. Attackers can send a single TCP packet on port 7624 with mismatched XML tags to trigger an unbounded sprintf() write into a fixed 1024-byte stack buffer in MsgQueue.cpp, terminating the daemon and disrupting all active client and driver sessions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71979.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71979
- https://www.vulncheck.com/advisories/indi-indiserver-stack-buffer-overflow-via-xml-tag-parsing
- https://github.com/indilib/indi/issues/2472
- https://github.com/indilib/indi/commit/96bbd7f564bbb128a129019e44eadd40dd49cff9
- https://github.com/indilib/indi
