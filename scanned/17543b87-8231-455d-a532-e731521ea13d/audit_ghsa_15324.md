# [M] request_store has Incorrect Default Permissions

## Summary
Severity: Medium
Advisory: GHSA-frp2-5qfc-7r8m
CVE: CVE-2024-43791
CWE: CWE-276
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-frp2-5qfc-7r8m
Type: github-advisory

## Affected
- RubyGems: `request_store` — affected >=1.3.2 <1.4.0

## Details
### Impact

The files published as part of request_store 1.3.2 have 0666 permissions, meaning that they are world-writable, which allows local users to execute arbitrary code.

This version was published in 2017, and most production environments do not allow access for local users, so the chances of this being exploited are very low, given that the vast majority of users will have upgraded, and those that have not, if any, are not likely to be exposed.

### Patches

I am not aware of any other version of the gem with incorrect permissions, so simply upgrading should fix the issue.

### Workarounds

You could chmod the files yourself, I guess.

### References

https://cwe.mitre.org/data/definitions/276.html

## References
- https://github.com/steveklabnik/request_store/security/advisories/GHSA-frp2-5qfc-7r8m
- https://nvd.nist.gov/vuln/detail/CVE-2024-43791
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/request_store/CVE-2024-43791.yml
- https://github.com/steveklabnik/request_store
