# [M] Cross-site Scripting in Sidekiq

## Summary
Severity: Medium
Advisory: GHSA-grh7-935j-hg6w
CVE: CVE-2021-30151
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-grh7-935j-hg6w
Type: github-advisory

## Affected
- RubyGems: `sidekiq` — affected >=0 <5.2.0
- RubyGems: `sidekiq` — affected >=6.0.0 <6.2.1

## Details
Sidekiq through 5.1.3 and 6.x through 6.2.0 allows XSS via the queue name of the live-poll feature when Internet Explorer is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30151
- https://github.com/mperham/sidekiq/issues/4852
- https://github.com/mperham/sidekiq/commit/64f70339d1dcf50a55c00d36bfdb61d97ec63ed8
- https://github.com/mperham/sidekiq
- https://lists.debian.org/debian-lts-announce/2022/03/msg00015.html
