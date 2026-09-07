# [M] Route Validation Bypass in call

## Summary
Severity: Medium
Advisory: GHSA-84fv-prrc-5ggr
CVE: CVE-2016-10543
CWE: CWE-20
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-84fv-prrc-5ggr
Type: github-advisory

## Affected
- npm: `call` — affected >=2.0.1 <3.0.2

## Details
Affected versions of `call` do not validate empty parameters, which may result in a bypass of route validation rules. 

## Proof of Concept

Routing Scheme:
```
/api/{param}/{param2}/details
```
Triggering Request Path:
```
/api///
```


## Recommendation

Update to version 3.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10543
- https://github.com/hapijs/hapi/issues/3228
- https://github.com/advisories/GHSA-84fv-prrc-5ggr
- https://www.npmjs.com/advisories/121
