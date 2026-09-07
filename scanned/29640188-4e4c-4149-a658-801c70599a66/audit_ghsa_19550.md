# [H] Umbraco has a Management API Vulnerability to Path Traversal With Authenticated Users

## Summary
Severity: High
Advisory: GHSA-q62r-8ppj-xvf4
CVE: CVE-2025-32017
CWE: CWE-22, CWE-23
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-q62r-8ppj-xvf4
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0--preview004 <14.3.4
- NuGet: `Umbraco.Cms` — affected >=15.0.0-rc1 <15.3.1

## Details
### Impact
Authenticated users to the Umbraco backoffice are able to craft management API request that exploit a path traversal vulnerability to upload files into a incorrect location.

### Patches
The issue affects Umbraco 14+ and is patched in 14.3.4 and 15.3.1.

### Workarounds
Umbraco supports the configuration of [allowed](https://docs.umbraco.com/umbraco-cms/reference/configuration/contentsettings#allowed-upload-file-extensions) and [disallowed file extensions](https://docs.umbraco.com/umbraco-cms/reference/configuration/contentsettings#disallowed-upload-file-extensions).  Using these options to allow only necessary file extensions significantly reduces the scope of the vulnerability.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-q62r-8ppj-xvf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-32017
- https://github.com/umbraco/Umbraco-CMS/commit/06a2a500b358ce15b1e228391eb60bd517c6e833
- https://github.com/umbraco/Umbraco-CMS/commit/d3c1443b14b1076faf13d1bcecc42860fdf5fad8
- https://github.com/umbraco/Umbraco-CMS
