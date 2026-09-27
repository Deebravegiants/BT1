# [H] Downloads Resources over HTTP in libxl

## Summary
Severity: High
Advisory: GHSA-7vrq-vg6p-32fw
CVE: CVE-2016-10585
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-7vrq-vg6p-32fw
Type: github-advisory

## Affected
- npm: `libxl` — affected >=0

## Details
Affected versions of `libxl` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `libxl`.


## Recommendation

The module author recommends installing the bindings using a pinned and verified version of SDK instead of the automated download. More information is available in the modules [README](https://www.npmjs.com/package/libxl).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10585
- https://github.com/DirtyHairy/node-libxl
- https://github.com/advisories/GHSA-7vrq-vg6p-32fw
- https://www.npmjs.com/advisories/178
