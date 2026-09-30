# [C] Puma HTTP Request/Response Smuggling vulnerability

## Summary
Severity: Critical
Advisory: GHSA-68xg-gqqm-vgj8
CVE: CVE-2023-40175
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-18
Source: https://github.com/advisories/GHSA-68xg-gqqm-vgj8
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <5.6.7
- RubyGems: `puma` — affected >=6.0.0 <6.3.1

## Details
### Impact
Prior to version 6.3.1, puma exhibited incorrect behavior when parsing chunked transfer encoding bodies and zero-length Content-Length headers in a way that allowed HTTP request smuggling.

The following vulnerabilities are addressed by this advisory:

* Incorrect parsing of trailing fields in chunked transfer encoding bodies
* Parsing of blank/zero-length Content-Length headers

### Patches
The vulnerability has been fixed in 6.3.1 and 5.6.7.

### Workarounds
No known workarounds.

### References
[HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling)

### For more information
If you have any questions or comments about this advisory:

Open an issue in [Puma](https://github.com/puma/puma)
See our [security policy](https://github.com/puma/puma/security/policy)

## References
- https://github.com/puma/puma/security/advisories/GHSA-68xg-gqqm-vgj8
- https://nvd.nist.gov/vuln/detail/CVE-2023-40175
- https://github.com/puma/puma/commit/690155e7d644b80eeef0a6094f9826ee41f1080a
- https://github.com/puma/puma/commit/7405a219801dcebc0ad6e0aa108d4319ca23f662
- https://github.com/puma/puma/commit/ed0f2f94b56982c687452504b95d5f1fbbe3eed1
- https://github.com/puma/puma
- https://github.com/puma/puma/releases/tag/v5.6.7
- https://github.com/puma/puma/releases/tag/v6.3.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2023-40175.yml
