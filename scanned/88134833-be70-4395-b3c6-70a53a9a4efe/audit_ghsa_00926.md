# [C] Cross-Site Scripting in swagger-ui

## Summary
Severity: Critical
Advisory: GHSA-p239-93f7-h6xf
CVE: CVE-2016-5682
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-p239-93f7-h6xf
Type: github-advisory

## Affected
- npm: `swagger-ui` — affected >=0 <2.2.1

## Details
Affected versions of `swagger-ui` contain a cross-site scripting vulnerability in the key names of a specific nested object in the JSON document.


## Proof of Concept
The vulnerable object structure is:
```
{
    "definitions": {
        "arbitraryVal": {
            "properties": {
                "<INJECTABLE_KEY_NAME>": "LoremIpsum"
                }
            }
        }
}
```
Malicious JSON documents can be loaded in by providing a URL to them in the `url` query string parameter.



## Recommendation

Update to version 2.2.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5682
- https://github.com/swagger-api/swagger-ui/issues/1865
- https://community.rapid7.com/community/infosec/blog/2016/09/02/r7-2016-19-persistent-xss-via-unescaped-parameters-in-swagger-ui
- https://github.com/swagger-api/swagger-ui
- https://www.npmjs.com/advisories/126
