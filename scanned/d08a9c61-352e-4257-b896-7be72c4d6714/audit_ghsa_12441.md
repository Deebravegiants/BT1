# [M] Resque Scheduler Reflected XSS In Delayed Jobs View

## Summary
Severity: Medium
Advisory: GHSA-9hmq-fm33-x4xx
CVE: CVE-2022-44303
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-9hmq-fm33-x4xx
Type: github-advisory

## Affected
- RubyGems: `resque-scheduler` — affected >=1.27.4 <4.10.2

## Details
### Impact

Resque Scheduler version 1.27.4 and above are affected by a cross-site scripting vulnerability. A remote attacker can inject javascript code to the "{schedule_job}" or "args" parameter in /resque/delayed/jobs/{schedule_job}?args={args_id} to execute javascript at client side.

### Patches

Fixed in v4.10.2

### Workarounds

No known workarounds at this time. It is recommended to not click on 3rd party or untrusted links to the resque-web interface until you have patched your application.

### References
* https://nvd.nist.gov/vuln/detail/CVE-2022-44303
* https://github.com/resque/resque-scheduler/issues/761
* https://github.com/resque/resque/issues/1885
* https://github.com/resque/resque-scheduler/pull/780
* https://github.com/resque/resque-scheduler/pull/783

## References
- https://github.com/resque/resque-scheduler/security/advisories/GHSA-9hmq-fm33-x4xx
- https://nvd.nist.gov/vuln/detail/CVE-2022-44303
- https://github.com/resque/resque-scheduler
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/resque-scheduler/CVE-2022-44303.yml
- https://trungvm.gitbook.io/cves/resque/resque-1.27.4-multiple-reflected-xss-in-resque-schedule-job
