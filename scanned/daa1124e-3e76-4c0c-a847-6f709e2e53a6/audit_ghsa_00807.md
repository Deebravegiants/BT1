# [M] Rosetta-Flash JSONP Vulnerability in hapi

## Summary
Severity: Medium
Advisory: GHSA-363h-vj6q-3cmj
CVE: CVE-2014-4671
CWE: CWE-352
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-363h-vj6q-3cmj
Type: github-advisory

## Affected
- npm: `hapi` — affected >=0 <6.1.0

## Details
This description taken from the pull request provided by Patrick Kettner.



Versions 6.1.0 and earlier of hapi are vulnerable to a rosetta-flash attack, which can be used by attackers to send data across domains and break the browser same-origin-policy.





## Recommendation

- Update hapi to version 6.1.1 or later.

Alternatively, a solution previously implemented by Google, Facebook, and Github is to prepend callbacks with an empty inline comment. This will cause the flash parser to break on invalid inputs and prevent the issue, and how the issue has been resolved internally in hapi.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4671
- https://github.com/spumko/hapi/pull/1766
- https://github.com/hapijs/hapi/commit/d47f57abf23bdaa84f61aed2bac94ae5f358afb7
- https://github.com/patrickkettner
- https://github.com/spumko/hapi
- https://www.npmjs.com/advisories/12
- http://helpx.adobe.com/security/products/flash-player/apsb14-17.html
- http://miki.it/blog/2014/7/8/abusing-jsonp-with-rosetta-flash
- http://rhn.redhat.com/errata/RHSA-2014-0860.html
- http://secunia.com/advisories/59774
- http://secunia.com/advisories/59837
- http://security.gentoo.org/glsa/glsa-201407-02.xml
- http://www.securityfocus.com/bid/68457
- http://www.securitytracker.com/id/1030533
