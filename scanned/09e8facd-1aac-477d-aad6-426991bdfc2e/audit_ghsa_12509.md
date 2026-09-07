# [M] Resque vulnerable to Reflected Cross Site Scripting through pathnames

## Summary
Severity: Medium
Advisory: GHSA-r8xx-8vm8-x6wj
CVE: CVE-2023-50724
CWE: CWE-233, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-r8xx-8vm8-x6wj
Type: github-advisory

## Affected
- RubyGems: `resque` — affected >=0 <2.1.0

## Details
### Impact

resque-web in resque versions before 2.1.0 is vulnerable to reflected XSS through the current_queue parameter in the path of the queues endpoint.

### Patches

v2.1.0

### Workarounds

No known workarounds at this time. It is recommended to not click on 3rd party or untrusted links to the resque-web interface until you have patched your application.

### References
https://github.com/resque/resque/issues/1679
https://github.com/resque/resque/pull/1687

## References
- https://github.com/resque/resque/security/advisories/GHSA-r8xx-8vm8-x6wj
- https://nvd.nist.gov/vuln/detail/CVE-2023-50724
- https://github.com/resque/resque/issues/1679
- https://github.com/resque/resque/pull/1687
- https://github.com/resque/resque/commit/e8e2367fff6990d13109ec2483a456a05fbf9811
- https://github.com/resque/resque
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/resque/CVE-2023-50724.yml
