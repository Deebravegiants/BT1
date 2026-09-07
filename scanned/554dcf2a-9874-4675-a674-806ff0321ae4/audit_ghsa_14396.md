# [M] Possible XSS Security Vulnerability in SafeBuffer#bytesplice

## Summary
Severity: Medium
Advisory: GHSA-pj73-v5mw-pm9j
CVE: CVE-2023-28120
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-03-15
Source: https://github.com/advisories/GHSA-pj73-v5mw-pm9j
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=7.0.0 <7.0.4.3
- RubyGems: `activesupport` — affected >=0 <6.1.7.3

## Details
There is a vulnerability in ActiveSupport if the new bytesplice method is called on a SafeBuffer with untrusted user input.
This vulnerability has been assigned the CVE identifier CVE-2023-28120.

Versions Affected: All. Not affected: None Fixed Versions: 7.0.4.3, 6.1.7.3

# Impact

ActiveSupport uses the SafeBuffer string subclass to tag strings as html_safe after they have been sanitized.
When these strings are mutated, the tag is should be removed to mark them as no longer being html_safe.

Ruby 3.2 introduced a new bytesplice method which ActiveSupport did not yet understand to be a mutation.
Users on older versions of Ruby are likely unaffected.

All users running an affected release and using bytesplice should either upgrade or use one of the workarounds immediately.

# Workarounds

Avoid calling bytesplice on a SafeBuffer (html_safe) string with untrusted user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28120
- https://github.com/rails/rails/commit/3cf23c3f891e2e81c977ea4ab83b62bc2a444b70
- https://discuss.rubyonrails.org/t/cve-2023-28120-possible-xss-security-vulnerability-in-safebuffer-bytesplice/82469
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2023-28120.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UPV6PVCX4VDJHLFFT42EXBBSGAWZICOW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZE5W4MH6IE4DV7GELDK6ISCSTFLHKSYO
- https://security.netapp.com/advisory/ntap-20240202-0006
- https://www.debian.org/security/2023/dsa-5389
