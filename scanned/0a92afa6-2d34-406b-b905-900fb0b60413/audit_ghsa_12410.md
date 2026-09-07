# [M] Resque vulnerable to reflected XSS in resque-web failed and queues lists

## Summary
Severity: Medium
Advisory: GHSA-gc3j-vvwf-4rp8
CVE: CVE-2023-50725
CWE: CWE-233, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-gc3j-vvwf-4rp8
Type: github-advisory

## Affected
- RubyGems: `resque` — affected >=0 <2.2.1

## Details
### Impact

The following paths in resque-web have been found to be vulnerable to reflected XSS:

```
/failed/?class=<script>alert(document.cookie)</script>
/queues/><img src=a onerror=alert(document.cookie)>
```

### Patches

v2.2.1

### Workarounds

No known workarounds at this time. It is recommended to not click on 3rd party or untrusted links to the resque-web interface until you have patched your application.

### References

https://github.com/resque/resque/pull/1790

## References
- https://github.com/resque/resque/security/advisories/GHSA-gc3j-vvwf-4rp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-50725
- https://github.com/resque/resque/pull/1790
- https://github.com/resque/resque/commit/ee99d2ed6cc75d9d384483b70c2d96d312115f07
- https://github.com/resque/resque
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/resque/CVE-2023-50725.yml
