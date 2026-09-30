# [M] Buttercup allows attackers to obtain the hash of the master password

## Summary
Severity: Medium
Advisory: GHSA-7cwq-p8cr-h9qg
CVE: CVE-2023-41646
CWE: CWE-916
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-7cwq-p8cr-h9qg
Type: github-advisory

## Affected
- npm: `buttercup` — affected >=2.20.3 <7.4.0

## Details
Buttercup allows attackers to obtain the hash of the master password for the password manager via accessing the file /vaults.json/.

This affects the Buttercup app up to version 2.20.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41646
- https://github.com/buttercup/buttercup-core/issues/336
- https://github.com/buttercup/buttercup-core/commit/77fbcdfe4caf57486a3c83c07fc6d36bb0e1d3e1
- https://buttercup.pw
- https://github.com/buttercup/buttercup-core
- https://github.com/tristao-marinho/CVE-2023-41646
