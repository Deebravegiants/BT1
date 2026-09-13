# [M] ALPINE-CVE-2026-50012

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-50012
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-50012
Type: osv

## Affected
- Alpine:v3.23: `squid` — affected >=0 <7.6-r0
- Alpine:v3.24: `squid` — affected >=0 <7.6-r0

## Details
Squid is a caching proxy for the Web. Prior to 7.6, due to an improper input validation bug in cache digest reply handling (peerDigestSwapInMask in src/peer_digest.cc), Squid is vulnerable to a heap-based buffer overflow: a cache digest's on-the-wire size may be larger than the mask_size declared within the digest, so a trusted peer sending a maliciously crafted reply to a cache_digest request message can trigger the overflow. This attack is limited to Squid instances compiled with the --enable-cache-digests option and configured with cache_peer entries. This issue is fixed in version 7.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-50012
