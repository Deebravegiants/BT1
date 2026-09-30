# [H] GrapesJsBuilder File Upload allows all file uploads

## Summary
Severity: High
Advisory: GHSA-5xw2-57jx-pgjp
CVE: CVE-2025-13827
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-5xw2-57jx-pgjp
Type: github-advisory

## Affected
- Packagist: `mautic/grapes-js-builder-bundle` — affected >=4.0.0 <4.4.18
- Packagist: `mautic/grapes-js-builder-bundle` — affected >=5.0.0 <5.2.9
- Packagist: `mautic/grapes-js-builder-bundle` — affected >=6.0.0 <6.0.7

## Details
### Summary

Arbitrary files can be uploaded via the GrapesJS Builder, as the types of files that can be uploaded are not restricted. 

### Impact

If the media folder is not restricted from running files this can lead to a remote code execution.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-5xw2-57jx-pgjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-13827
- https://github.com/mautic/mautic
