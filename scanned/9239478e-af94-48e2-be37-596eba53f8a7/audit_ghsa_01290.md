# [H] Prototype Pollution in node-forge

## Summary
Severity: High
Advisory: GHSA-92xj-mqp7-vmcj
CVE: CVE-2020-7720
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:P/RL:O/RC:C (CVSS_V3)
Published: 2020-09-14
Source: https://github.com/advisories/GHSA-92xj-mqp7-vmcj
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <0.10.0

## Details
The package node-forge before 0.10.0 is vulnerable to Prototype Pollution via the util.setPath function. Note: version 0.10.0 is a breaking change removing the vulnerable functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7720
- https://github.com/digitalbazaar/forge/commit/6a1e3ef74f6eb345bcff1b82184201d1e28b6756
- https://github.com/digitalbazaar/forge
- https://github.com/digitalbazaar/forge/blob/master/CHANGELOG.md
- https://github.com/digitalbazaar/forge/blob/master/CHANGELOG.md#removed
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-609293
- https://snyk.io/vuln/SNYK-JS-NODEFORGE-598677
