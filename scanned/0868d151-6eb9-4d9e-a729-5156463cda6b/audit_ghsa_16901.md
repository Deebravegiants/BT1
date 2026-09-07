# [H] Mautic Sensitive Data Exposure due to inadequate user permission settings

## Summary
Severity: High
Advisory: GHSA-qjx3-2g35-6hv8
CVE: CVE-2022-25776
CWE: CWE-276, CWE-280
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-qjx3-2g35-6hv8
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.2 <4.4.12
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.0.4

## Details
### Impact
Prior to the patched version, logged in users of Mautic are able to access areas of the application that they should be prevented from accessing.

Users could potentially access sensitive data such as names and surnames, company names and stage names.

### Patches
Update to 4.4.12 and 5.0.4

### Workarounds
No

### References
https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-qjx3-2g35-6hv8
- https://nvd.nist.gov/vuln/detail/CVE-2022-25776
- https://github.com/mautic/mautic/commit/22bdd0796ca6e1e985708b89ad5c07147630fecd
- https://github.com/mautic/mautic/commit/2cc4af975fe01c264d439acc1451c936e7114644
- https://github.com/mautic/mautic
