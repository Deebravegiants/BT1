# [M] Umbraco Vulnerable to By-Pass of Configured Allowed Extensions for File Uploads

## Summary
Severity: Medium
Advisory: GHSA-fr6r-p8hv-x3c4
CVE: CVE-2025-48953
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-fr6r-p8hv-x3c4
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <15.4.2

## Details
### Impact
Via a manipulated API request it's possible to upload a file that doesn't adhere with the configured allowable file extensions.

### Patches
Patched in 15.4.2 and 16.0.0.

### Workarounds
None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-fr6r-p8hv-x3c4
- https://nvd.nist.gov/vuln/detail/CVE-2025-48953
- https://github.com/umbraco/Umbraco-CMS/commit/d920e93d1ee29dc3301697e444f53e8cd5db3cf9
- https://github.com/umbraco/Umbraco-CMS
