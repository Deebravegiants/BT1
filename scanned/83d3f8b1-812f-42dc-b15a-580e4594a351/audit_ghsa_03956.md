# [H] Prototype Pollution in mpath

## Summary
Severity: High
Advisory: GHSA-h466-j336-74wx
CVE: CVE-2018-16490
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-h466-j336-74wx
Type: github-advisory

## Affected
- npm: `mpath` — affected >=0 <0.5.1

## Details
Versions of `mpath` before 0.5.1 are vulnerable to prototype pollution. Provided certain input `mpath` can add or modify properties of the `Object` prototype. These properties will be present on all objects.


## Recommendation

Update to version `0.5.1` or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16490
- https://hackerone.com/reports/390860
- https://github.com/advisories/GHSA-h466-j336-74wx
- https://www.npmjs.com/advisories/779
