# [M] XSS in Bleach when noscript and raw tag whitelisted

## Summary
Severity: Medium
Advisory: GHSA-q65m-pv3f-wr5r
CVE: CVE-2020-6802
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-q65m-pv3f-wr5r
Type: github-advisory

## Affected
- PyPI: `bleach` — affected >=0 <3.1.1

## Details
### Impact

A [mutation XSS](https://cure53.de/fp170.pdf) affects users calling `bleach.clean` with `noscript` and a raw tag (see below) in the allowed/whitelisted tags option.

### Patches

v3.1.1

### Workarounds

* modify `bleach.clean` calls to not whitelist `noscript` and one or more of the following raw tags:

```
title
textarea
script
style
noembed
noframes
iframe
xmp
```

* A strong [Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) without `unsafe-inline` and `unsafe-eval` [`script-src`s](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src)) will also help mitigate the risk.

### References

* https://bugzilla.mozilla.org/show_bug.cgi?id=1615315
* https://cure53.de/fp170.pdf
* https://nvd.nist.gov/vuln/detail/CVE-2020-6802
* https://www.checkmarx.com/blog/vulnerabilities-discovered-in-mozilla-bleach

### Credits

* Reported by [Yaniv Nizry](https://twitter.com/ynizry) from the CxSCA AppSec group at Checkmarx

### For more information

If you have any questions or comments about this advisory:

* Open an issue at [https://github.com/mozilla/bleach/issues](https://github.com/mozilla/bleach/issues)
* Email us at [security@mozilla.org](mailto:security@mozilla.org)

## References
- https://github.com/mozilla/bleach/security/advisories/GHSA-q65m-pv3f-wr5r
- https://nvd.nist.gov/vuln/detail/CVE-2020-6802
- https://github.com/mozilla/bleach/commit/f77e0f6392177a06e46a49abd61a4d9f035e57fd
- https://advisory.checkmarx.net/advisory/CX-2020-4276
- https://bugzilla.mozilla.org/show_bug.cgi?id=1615315
- https://cure53.de/fp170.pdf
- https://github.com/mozilla/bleach
- https://github.com/pypa/advisory-database/tree/main/vulns/bleach/PYSEC-2020-27.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/72R4VFFHDRSQMNT7IZU3X2755ZP4HGNI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCNLM2MGQTOLCIVVYS2Z5S7KOQJR5JC4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YTULPQB7HVPPYWEYVNHJGDTSPVIDHIZX
- https://www.checkmarx.com/blog/vulnerabilities-discovered-in-mozilla-bleach
