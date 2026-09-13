# [M] mofh Vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: Medium
Advisory: GHSA-7r9x-qrpr-3cxw
CWE: CWE-611
Ecosystem: PyPI
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-7r9x-qrpr-3cxw
Type: github-advisory

## Affected
- PyPI: `mofh` — affected >=0 <1.0.1

## Details
The `xml.etree.ElementTree` module that mofh used up until version `1.0.1` implements a simple and efficient API for parsing and creating XML data. But it makes the application vulnerable to:

- [Billion Laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack): It is a type of denial-of-service attack aimed at XML parsers. It uses multiple levels of nested entities. If one large entity is repeated with a couple of thousand chars repeatedly, the parser gets overwhelmed.  
- [Quadratic blowup attack](https://www.acunetix.com/vulnerabilities/web/xml-quadratic-blowup-denial-of-service-attack/): It is similar to a Billion Laughs attack. It abuses entity expansion, too. Instead of nested entities, it repeats one large entity with a couple of thousand chars repeatedly.

The Problem has been patched starting from version `1.0.1` by utilising the `defusedxml` package instead of `xml.etree.ElementTree`.

### Workarounds
For this vulnerability to be exploited the user must be using a custom API URL, which has to be manually given using the `api_url` argument, or MyOwnFreeHost's API must be hacked. So, if the user did not use a custom API URL they _should_ be fine, however, upgrading is still advised.

Another workaround could be to call `defusedxml.defuse_stdlib()` before making any requests using the client.

## References
- https://github.com/Wallvon/mofh/security/advisories/GHSA-7r9x-qrpr-3cxw
- https://github.com/Wallvon/mofh/commit/da0d33cfd368e2f237ab28bf7a7f00e3d281005a
- https://github.com/Wallvon/mofh
- https://www.acunetix.com/vulnerabilities/web/xml-quadratic-blowup-denial-of-service-attack
