# [M] memory leak flaw was found in ruby-magick

## Summary
Severity: Medium
Advisory: GHSA-frgf-8jr5-j2jv
CVE: CVE-2023-5349
CWE: CWE-400, CWE-401
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-10-30
Source: https://github.com/advisories/GHSA-frgf-8jr5-j2jv
Type: github-advisory

## Affected
- RubyGems: `rmagick` — affected >=0 <5.3.0

## Details
A memory leak flaw was found in ruby-magick, an interface between Ruby and ImageMagick. This issue can lead to a denial of service (DOS) by memory exhaustion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5349
- https://github.com/rmagick/rmagick/issues/1401
- https://github.com/rmagick/rmagick/pull/1406
- https://github.com/rmagick/rmagick/commit/02f37ca0d6c2b8fff316e0668efa690f5c90a429
- https://github.com/rmagick/rmagick/commit/fec7a7e639ae565386f7615155dbcf49b957b64a
- https://access.redhat.com/security/cve/CVE-2023-5349
- https://bugzilla.redhat.com/show_bug.cgi?id=2247064
- https://github.com/advisories/GHSA-frgf-8jr5-j2jv
- https://github.com/rmagick/rmagick
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rmagick/CVE-2023-5349.yml
- https://lists.debian.org/debian-lts-announce/2023/10/msg00030.html
- https://lists.debian.org/debian-lts-announce/2026/01/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S3XMQ2KWPYGT447EKPENGXXHKAQ5NUWF
