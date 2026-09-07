# [M] Cross-Site Scripting (XSS) in restify

## Summary
Severity: Medium
Advisory: GHSA-qw3g-35hc-fcrh
CVE: CVE-2017-16018
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-qw3g-35hc-fcrh
Type: github-advisory

## Affected
- npm: `restify` — affected >=2.0.0 <4.1.0

## Details
Affected versions of `restify` are susceptible to a cross-site scripting vulnerability when using URL encoded script tags in a non-existent URL.

## Proof of Concept:

Request
```
https://localhost:3000/no5_such3_file7.pl?%22%3E%3Cscript%3Ealert(73541);%3C/script%3E
```

Will be included in response:

```<script>alert(73541);</script>```


## Recommendation

Update to version 4.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16018
- https://github.com/restify/node-restify/issues/1018
- https://github.com/advisories/GHSA-qw3g-35hc-fcrh
- https://www.npmjs.com/advisories/314
