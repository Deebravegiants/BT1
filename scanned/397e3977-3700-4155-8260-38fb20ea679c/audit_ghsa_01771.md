# [M] Bleach vulnerable to mutation XSS via whitelisted math or svg and raw tag

## Summary
Severity: Medium
Advisory: GHSA-m6xf-fq7q-8743
CVE: CVE-2020-6816
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-03-24
Source: https://github.com/advisories/GHSA-m6xf-fq7q-8743
Type: github-advisory

## Affected
- PyPI: `bleach` — affected >=0 <3.1.2

## Details
### Impact

A [mutation XSS](https://cure53.de/fp170.pdf) affects users calling `bleach.clean` with all of:

* the `svg` or `math` in the allowed/whitelisted tags
* an RCDATA tag (see below) in the allowed/whitelisted tags
* the keyword argument `strip=False`

### Patches

Users are encouraged to upgrade to bleach v3.1.2 or greater.

### Workarounds

* modify `bleach.clean` calls to use `strip=True`, or not whitelist `math` or `svg` tags and one or more of the following tags:

```
script
noscript
style
noframes
xmp
noembed
iframe
```

* A strong [Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) without `unsafe-inline` and `unsafe-eval` [`script-src`s](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src)) will also help mitigate the risk.

### References

* https://bugzilla.mozilla.org/show_bug.cgi?id=1621692
* https://cure53.de/fp170.pdf
* https://nvd.nist.gov/vuln/detail/CVE-2020-6816
* https://www.checkmarx.com/blog/vulnerabilities-discovered-in-mozilla-bleach

### Credits

* Reported by [Yaniv Nizry](https://twitter.com/ynizry) from the CxSCA AppSec group at Checkmarx

### For more information

If you have any questions or comments about this advisory:

* Open an issue at [https://github.com/mozilla/bleach/issues](https://github.com/mozilla/bleach/issues)
* Email us at [security@mozilla.org](mailto:security@mozilla.org)

## References
- https://github.com/mozilla/bleach/security/advisories/GHSA-m6xf-fq7q-8743
- https://nvd.nist.gov/vuln/detail/CVE-2020-6816
- https://advisory.checkmarx.net/advisory/CX-2020-4277
- https://github.com/mozilla/bleach
- https://github.com/mozilla/bleach/releases/tag/v3.1.2
- https://github.com/pypa/advisory-database/tree/main/vulns/bleach/PYSEC-2020-28.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EDQU2SZLZMSSACCBUBJ6NOSRNNBDYFW5
- https://www.checkmarx.com/blog/vulnerabilities-discovered-in-mozilla-bleach
