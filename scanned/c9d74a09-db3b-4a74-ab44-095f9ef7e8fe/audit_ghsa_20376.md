# [M] Mechanize before v2.8.5 vulnerable to authorization header leak on port redirect

## Summary
Severity: Medium
Advisory: GHSA-64qm-hrgp-pgr9
CVE: CVE-2022-31033
CWE: CWE-200, CWE-522
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-64qm-hrgp-pgr9
Type: github-advisory

## Affected
- RubyGems: `mechanize` — affected >=0 <2.8.5

## Details
**Summary**

Mechanize (rubygem) `< v2.8.5` leaks the `Authorization` header after a redirect to a different port on the same site.

**Mitigation**

Upgrade to Mechanize v2.8.5 or later.

**Notes**

See [https://curl.se/docs/CVE-2022-27776.html](CVE-2022-27776) for a similar vulnerability in curl.

Cookies are shared with a server at a different port on the same site, per https://datatracker.ietf.org/doc/html/rfc6265#section-8.5 which states in part:

> Cookies do not provide isolation by port.  If a cookie is readable
> by a service running on one port, the cookie is also readable by a
> service running on another port of the same server.  If a cookie is
> writable by a service on one port, the cookie is also writable by a
> service running on another port of the same server.  For this
> reason, servers SHOULD NOT both run mutually distrusting services on
> different ports of the same host and use cookies to store security-
> sensitive information.

## References
- https://github.com/sparklemotion/mechanize/security/advisories/GHSA-64qm-hrgp-pgr9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31033
- https://github.com/sparklemotion/mechanize/commit/c7fe6996a5b95f9880653ba3bc548a8d4ef72317
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mechanize/CVE-2022-31033.yml
- https://github.com/sparklemotion/mechanize
