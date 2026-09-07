# [M] Doorkeeper is vulnerable to stored XSS and code execution

## Summary
Severity: Medium
Advisory: GHSA-hwhh-2fwm-cfgw
CVE: CVE-2018-1000088
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-03-13
Source: https://github.com/advisories/GHSA-hwhh-2fwm-cfgw
Type: github-advisory

## Affected
- RubyGems: `doorkeeper` — affected >=2.1.0 <4.2.6

## Details
Doorkeeper version 2.1.0 through 4.2.5 contains a Cross Site Scripting (XSS) vulnerability in web view's OAuth app form, user authorization prompt web view that can result in Stored XSS on the OAuth Client's name will cause users interacting with it will execute payload. This attack appear to be exploitable via The victim must be tricked to click an opaque link to the web view that runs the XSS payload. A malicious version virtually indistinguishable from a normal link. This vulnerability appears to have been fixed in 4.2.6, 4.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000088
- https://github.com/doorkeeper-gem/doorkeeper/issues/969
- https://github.com/doorkeeper-gem/doorkeeper/pull/970
- https://github.com/rubysec/ruby-advisory-db/pull/328/files
- https://github.com/doorkeeper-gem/doorkeeper/commit/7b1a8373ecd69768c896000c7971dbf48948c1b5
- https://blog.justinbull.ca/cve-2018-1000088-stored-xss-in-doorkeeper
- https://github.com/doorkeeper-gem/doorkeeper
- https://github.com/doorkeeper-gem/doorkeeper/releases/tag/v4.3.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/doorkeeper/CVE-2018-1000088.yml
