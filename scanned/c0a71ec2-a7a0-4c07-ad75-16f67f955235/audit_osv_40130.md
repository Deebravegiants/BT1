# [M] Squid: Memory corruption in cache_digest reply handling

## Summary
Severity: Medium
Advisory: CVE-2026-50012
Aliases: GHSA-5vmx-9x64-9284
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-50012
Type: osv

## Details
Squid is a caching proxy for the Web. Prior to 7.6, due to an improper input validation bug in cache digest reply handling (peerDigestSwapInMask in src/peer_digest.cc), Squid is vulnerable to a heap-based buffer overflow: a cache digest's on-the-wire size may be larger than the mask_size declared within the digest, so a trusted peer sending a maliciously crafted reply to a cache_digest request message can trigger the overflow. This attack is limited to Squid instances compiled with the --enable-cache-digests option and configured with cache_peer entries. This issue is fixed in version 7.6.

## References
- https://github.com/squid-cache/squid/releases/tag/SQUID_7_6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50012.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-5vmx-9x64-9284
- https://nvd.nist.gov/vuln/detail/CVE-2026-50012
- https://github.com/squid-cache/squid/commit/19fcfe922717c8b255270c032dcde4071c003bcd
- https://github.com/squid-cache/squid/pull/2423
