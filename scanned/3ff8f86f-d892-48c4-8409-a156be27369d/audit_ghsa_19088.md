# [H] Mautic allows Improper Authorization in Reporting API

## Summary
Severity: High
Advisory: GHSA-8xv7-g2q3-fqgc
CVE: CVE-2024-47053
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-26
Source: https://github.com/advisories/GHSA-8xv7-g2q3-fqgc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.1 <5.2.3

## Details
### Summary

This advisory addresses an authorization vulnerability in Mautic's HTTP Basic Authentication implementation. This flaw could allow unauthorized access to sensitive report data.

* **Improper Authorization:** An authorization flaw exists in Mautic's API Authorization implementation. Any authenticated user, regardless of assigned roles or permissions, can access all reports and their associated data via the API.  This bypasses the intended access controls governed by the "Reporting Permissions > View Own" and "Reporting Permissions > View Others" permissions, which should restrict access to non-System Reports. 

### Mitigation

Please update to Mautic 5.2.3 or later

### Workarounds

 Disable the API in Mautic. See [documentation](https://docs.mautic.org/en/5.2/configuration/settings.html#api-settings).

### References
https://cwe.mitre.org/data/definitions/285.html
https://docs.mautic.org/en/5.2/configuration/settings.html#api-settings

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-8xv7-g2q3-fqgc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47053
- https://github.com/mautic/mautic/commit/9d7ee57c92502ef77cddb091011c5ffef14b11ee
- https://cwe.mitre.org/data/definitions/287.html
- https://docs.mautic.org/en/5.2/configuration/settings.html#api-settings
- https://github.com/mautic/mautic
