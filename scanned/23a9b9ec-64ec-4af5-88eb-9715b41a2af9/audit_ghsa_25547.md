# [M] XSS Vulnerability in Action View tag helpers

## Summary
Severity: Medium
Advisory: GHSA-ch3h-j2vf-95pv
CVE: CVE-2022-27777
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-ch3h-j2vf-95pv
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=0 <5.2.7.1
- RubyGems: `actionview` — affected >=6.0.0 <6.0.4.8
- RubyGems: `actionview` — affected >=6.1.0 <6.1.5.1
- RubyGems: `actionview` — affected >=7.0.0 <7.0.2.4

## Details
There is a possible XSS vulnerability in Action View tag helpers. Passing untrusted input as hash keys can lead to a possible XSS vulnerability. This vulnerability has been assigned the CVE identifier CVE-2022-27777.

Versions Affected:  ALL
Not affected:       NONE
Fixed Versions:     7.0.2.4, 6.1.5.1, 6.0.4.8, 5.2.7.1

## Impact

If untrusted data is passed as the hash key for tag attributes, there is a possibility that the untrusted data may not be properly escaped which can lead to an XSS vulnerability.

Impacted code will look something like this:

```
check_box_tag('thename', 'thevalue', false, aria: { malicious_input => 'thevalueofaria' })
```

Where the "malicious_input" variable contains untrusted data.

All users running an affected release should either upgrade or use one of the workarounds immediately.

## Releases

The FIXED releases are available at the normal locations.

## Workarounds

Escape the untrusted data before using it as a key for tag helper methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27777
- https://github.com/rails/rails/commit/649516ce0feb699ae06a8c5e81df75d460cc9a85
- https://discuss.rubyonrails.org/t/cve-2022-27777-possible-xss-vulnerability-in-action-view-tag-helpers/80534
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2022-27777.yml
- https://groups.google.com/g/ruby-security-ann/c/9wJPEDv-iRw
- https://lists.debian.org/debian-lts-announce/2022/09/msg00002.html
- https://rubyonrails.org/2022/4/26/Rails-7-0-2-4-6-1-5-1-6-0-4-8-and-5-2-7-1-have-been-released
- https://www.debian.org/security/2023/dsa-5372
