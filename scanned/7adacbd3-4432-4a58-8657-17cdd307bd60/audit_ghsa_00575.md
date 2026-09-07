# [H] XSS in Data URI in remarkable

## Summary
Severity: High
Advisory: GHSA-mrmf-qwxg-7c3h
CVE: CVE-2017-16006
CWE: CWE-79
Ecosystem: npm
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-mrmf-qwxg-7c3h
Type: github-advisory

## Affected
- npm: `remarkable` — affected >=0 <1.7.0

## Details
Affected versions of `remarkable` are vulnerable to cross-site scripting. Vulnerable versions of the package allow the use of `data:` URIs in links, and can therefore execute javascript. 


## Proof of Concept

```markdown
[link](data:text/html,<script>alert('0')</script>)
```


## Recommendation

Update to v1.7.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16006
- https://github.com/jonschlinkert/remarkable/issues/227
- https://github.com/advisories/GHSA-mrmf-qwxg-7c3h
- https://www.npmjs.com/advisories/319
