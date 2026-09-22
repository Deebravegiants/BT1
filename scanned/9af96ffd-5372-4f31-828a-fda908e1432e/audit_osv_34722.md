# [H] (conda) Constructor: Excessive permissions during and after installation

## Summary
Severity: High
Advisory: CVE-2025-64343
Aliases: GHSA-vvpr-2qg4-2mrq
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-64343
Type: osv

## Details
(conda) Constructor is a tool that enables users to create installers for conda package collections. In versions 3.12.2 and below, the  installation directory inherits permissions from its parent directory. Outside of restricted directories, the permissions are very permissive and often allow write access by authenticated users. Any logged in user can make modifications during the installation for both single-user and all-user installations. This constitutes a local attack vector if the installation is in a directory local users have access to. For single-user installations in a shared directory, these permissions persist after the installation. This issue is fixed in version 3.13.0.

## References
- https://github.com/conda/constructor/releases/tag/3.13.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64343.json
- https://github.com/conda/constructor/security/advisories/GHSA-vvpr-2qg4-2mrq
- https://nvd.nist.gov/vuln/detail/CVE-2025-64343
- https://github.com/conda/constructor/commit/c368383710a7c2b81ad1b0ecb9724b38d3577447
