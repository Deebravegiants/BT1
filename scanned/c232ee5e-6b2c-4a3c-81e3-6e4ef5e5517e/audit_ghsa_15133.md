# [H] D-Tale server-side request forgery through Web uploads

## Summary
Severity: High
Advisory: GHSA-7hfx-h3j3-rwq4
CVE: CVE-2024-21642
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-05
Source: https://github.com/advisories/GHSA-7hfx-h3j3-rwq4
Type: github-advisory

## Affected
- PyPI: `dtale` — affected >=0 <3.9.0

## Details
### Impact
Users hosting D-Tale publicly can be vulnerable to server-side request forgery (SSRF) allowing attackers to access files on the server.

### Patches
Users should upgrade to version 3.9.0 where the "Load From the Web" input is turned off by default. You can find out more information on how to turn it back on [here](https://github.com/man-group/dtale?tab=readme-ov-file#load-data--sample-datasets)

### Workarounds
The only workaround for versions earlier than 3.9.0 is to only host D-Tale to trusted users.

### References
See "Load Data & Sample Datasets" [documentation](https://github.com/man-group/dtale?tab=readme-ov-file#load-data--sample-datasets)

## References
- https://github.com/man-group/dtale/security/advisories/GHSA-7hfx-h3j3-rwq4
- https://nvd.nist.gov/vuln/detail/CVE-2024-21642
- https://github.com/man-group/dtale/commit/954f6be1a06ff8629ead2c85c6e3f8e2196b3df2
- https://github.com/man-group/dtale
- https://github.com/man-group/dtale?tab=readme-ov-file#load-data--sample-datasets
