# [C] ActiveSupport potentially unintended unmarshalling of user-provided objects in MemCacheStore and RedisCacheStore

## Summary
Severity: Critical
Advisory: GHSA-2p68-f74v-9wc6
CVE: CVE-2020-8165
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-26
Source: https://github.com/advisories/GHSA-2p68-f74v-9wc6
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=5.0.0 <5.2.4.3
- RubyGems: `activesupport` — affected >=6.0.0 <6.0.3.1

## Details
In ActiveSupport, there is potentially unexpected behaviour in the MemCacheStore and RedisCacheStore where, when
untrusted user input is written to the cache store using the `raw: true` parameter, re-reading the result
from the cache can evaluate the user input as a Marshalled object instead of plain text. Vulnerable code looks like:

```
data = cache.fetch("demo", raw: true) { untrusted_string }
```
Versions Affected:  rails < 5.2.5, rails < 6.0.4
Not affected:       Applications not using MemCacheStore or RedisCacheStore. Applications that do not use the `raw` option when storing untrusted user input.
Fixed Versions:     rails >= 5.2.4.3, rails >= 6.0.3.1
  
Impact
------
Unmarshalling of untrusted user input can have impact up to and including RCE. At a minimum,
this vulnerability allows an attacker to inject untrusted Ruby objects into a web application.
In addition to upgrading to the latest versions of Rails, developers should ensure that whenever
they are calling `Rails.cache.fetch` they are using consistent values of the `raw` parameter for both
reading and writing, especially in the case of the RedisCacheStore which does not, prior to these changes,
detect if data was serialized using the raw option upon deserialization.

Workarounds
-----------
It is recommended that application developers apply the suggested patch or upgrade to the latest release as
soon as possible. If this is not possible, we recommend ensuring that all user-provided strings cached using
the `raw` argument should be double-checked to ensure that they conform to the expected format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8165
- https://hackerone.com/reports/413388
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2020-8165.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/bv6fW4S0Y1c
- https://groups.google.com/g/rubyonrails-security/c/bv6fW4S0Y1c
- https://lists.debian.org/debian-lts-announce/2020/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00013.html
- https://security.netapp.com/advisory/ntap-20250509-0002
- https://weblog.rubyonrails.org/2020/5/18/Rails-5-2-4-3-and-6-0-3-1-have-been-released
- https://www.debian.org/security/2020/dsa-4766
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00034.html
