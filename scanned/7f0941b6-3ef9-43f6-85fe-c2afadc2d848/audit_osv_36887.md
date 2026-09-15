# [M] Stalwart Mail Server has Out-of-Memory Denial of Service via Malformed Nested MIME Messages

## Summary
Severity: Medium
Advisory: CVE-2026-26312
Aliases: GHSA-jm95-876q-c9gw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26312
Type: osv

## Details
Stalwart is a mail and collaboration server. A denial-of-service vulnerability exists in Stalwart Mail Server versions 0.13.0 through 0.15.4 where accessing a specially crafted email containing malformed nested `message/rfc822` MIME parts via IMAP or JMAP causes excessive CPU and memory consumption, potentially leading to an out-of-memory condition and server crash. The malformed structure causes the `mail-parser` crate to produce cyclical references in its parsed representation, which Stalwart then follows indefinitely. Version 0.15.5 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26312.json
- https://github.com/stalwartlabs/stalwart/security/advisories/GHSA-jm95-876q-c9gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-26312
