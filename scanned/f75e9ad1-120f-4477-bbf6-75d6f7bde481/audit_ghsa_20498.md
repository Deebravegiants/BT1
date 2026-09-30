# [H] Denial of service in sidekiq

## Summary
Severity: High
Advisory: GHSA-jrfj-98qg-qjgv
CVE: CVE-2022-23837
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-jrfj-98qg-qjgv
Type: github-advisory

## Affected
- RubyGems: `sidekiq` — affected >=6.0.0 <6.4.0
- RubyGems: `sidekiq` — affected >=0 <5.2.10

## Details
In `api.rb` in Sidekiq before 6.4.0 and 5.2.10, there is no limit on the number of days when requesting stats for the graph. This overloads the system, affecting the Web UI, and makes it unavailable to users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23837
- https://github.com/rubysec/ruby-advisory-db/pull/495
- https://github.com/mperham/sidekiq/commit/7785ac1399f1b28992adb56055f6acd88fd1d956
- https://github.com/TUTUMSPACE/exploits/blob/main/sidekiq.md
- https://github.com/mperham/sidekiq
- https://lists.debian.org/debian-lts-announce/2022/03/msg00015.html
