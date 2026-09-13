# [C] CVE-2026-43798

## Summary
Severity: Critical
Advisory: CVE-2026-43798
Aliases: GHSA-998x-vgvp-xwpc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-43798
Type: osv

## Details
A single crafted SSH message gives an unauthenticated network attacker an out-of-bounds stack write of attacker-controlled length and content against any application built on swift-nio-ssh. This vulnerability is addressed in swift-nio-ssh version 0.14.1.

## References
- https://github.com/apple/swift-nio-ssh/security/advisories/GHSA-998x-vgvp-xwpc
