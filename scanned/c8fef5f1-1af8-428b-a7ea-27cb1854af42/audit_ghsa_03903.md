# [H] Downloads Resources over HTTP in phantomjs-cheniu

## Summary
Severity: High
Advisory: GHSA-w364-8vfv-gvf5
CVE: CVE-2016-10661
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-w364-8vfv-gvf5
Type: github-advisory

## Affected
- npm: `phantomjs-cheniu` — affected >=0

## Details
Affected versions of `phantomjs-cheniu` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `phantomjs-cheniu`.


## Recommendation

No patch is currently available for this vulnerability.

As this package is just a fork of Medium's [`phantomjs-prebuilt`](https://github.com/Medium/phantomjs) package, the best mitigation is currently to install the `Medium` version of [`phantomjs-prebuilt`](https://github.com/Medium/phantomjs). This can be done via the following command:
```
npm i phantomjs-prebuilt
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10661
- https://github.com/advisories/GHSA-w364-8vfv-gvf5
- https://www.npmjs.com/advisories/262
