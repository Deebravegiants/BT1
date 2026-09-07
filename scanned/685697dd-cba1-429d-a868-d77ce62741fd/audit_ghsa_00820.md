# [H] Content Injection in remarkable

## Summary
Severity: High
Advisory: GHSA-f9vc-q3hh-qhfv
CVE: CVE-2014-10065
CWE: CWE-94
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-f9vc-q3hh-qhfv
Type: github-advisory

## Affected
- npm: `remarkable` — affected >=0 <1.4.1

## Details
Versions 1.4.0 and earlier of `remarkable` are affected by a cross-site scripting vulnerability. This occurs because vulnerable versions of `remarkable` did not properly whitelist link protocols, and consequently allowed `javascript:` to be used. 


### Proof of Concept

Markdown Source:
```
[link](<javascript:alert(1)>)
```

Rendered HTML:
```
<a href="javascript:alert(1)">link</a>
```


## Recommendation

Update to version 1.4.1 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10065
- https://github.com/jonschlinkert/remarkable/issues/97
- https://github.com/jonschlinkert/remarkable/commit/d54ed887f4997221cd7cb9790e953a83c504de36
- https://www.npmjs.com/advisories/30
