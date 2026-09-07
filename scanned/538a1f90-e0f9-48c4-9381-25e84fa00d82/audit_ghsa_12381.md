# [M] Resque vulnerable to reflected XSS in Queue Endpoint

## Summary
Severity: Medium
Advisory: GHSA-r9mq-m72x-257g
CVE: CVE-2023-50727
CWE: CWE-233, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-r9mq-m72x-257g
Type: github-advisory

## Affected
- RubyGems: `resque` — affected >=0 <2.6.0

## Details
### Impact

Reflected XSS can be performed using the current_queue portion of the path on the /queues endpoint of resque-web.

### Patches

v2.6.0

### Workarounds

No known workarounds at this time. It is recommended to not click on 3rd party or untrusted links to the resque-web interface until you have patched your application.

### References

https://github.com/resque/resque/pull/1865

## References
- https://github.com/resque/resque/security/advisories/GHSA-r9mq-m72x-257g
- https://nvd.nist.gov/vuln/detail/CVE-2023-50727
- https://github.com/resque/resque/pull/1865
- https://github.com/resque/resque/commit/7623b8dfbdd0a07eb04b19fb25b16a8d6f087f9a
- https://github.com/resque/resque
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/resque/CVE-2023-50727.yml
