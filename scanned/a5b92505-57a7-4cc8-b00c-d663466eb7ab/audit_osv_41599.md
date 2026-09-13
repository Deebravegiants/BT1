# [M] CoreDNS: rewrite-plugin EDNS0 response-revert nil-pointer panic (remote DoS) when a downstream plugin returns a response with no OPT record

## Summary
Severity: Medium
Advisory: CVE-2026-62299
Aliases: GHSA-9pmm-cxww-rrr7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-62299
Type: osv

## Details
CoreDNS is a DNS server written in Go. Prior to 1.14.5, the CoreDNS rewrite plugin supports edns0 rewrite rules with an optional revert flag, and two response rules, edns0SetResponseRule and edns0ReplaceResponseRule[T] in plugin/rewrite/edns0.go, call res.IsEdns0() and immediately dereference the returned *dns.OPT without a nil check when a downstream plugin returns a response with no OPT record. A remote, unauthenticated client can send a single ordinary DNS query matching a rewrite edns0 <local|nsid|subnet> <set|append|replace> ... revert rule, causing ResponseReverter in plugin/rewrite/reverter.go to panic, return SERVFAIL, and degrade availability, or crash the CoreDNS process if the debug directive disables recovery. This issue is fixed in version 1.14.5.

## References
- https://github.com/coredns/coredns/releases/tag/v1.14.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62299.json
- https://github.com/coredns/coredns/security/advisories/GHSA-9pmm-cxww-rrr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-62299
- https://github.com/coredns/coredns/commit/fc447d0658b093edc8cd29a6b171216a44a644c2
- https://github.com/coredns/coredns/pull/8190
