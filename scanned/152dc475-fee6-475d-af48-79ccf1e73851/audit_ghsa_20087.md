# [M] binwalk vulnerable to UNIX Symbolic Link (Symlink) Following

## Summary
Severity: Medium
Advisory: GHSA-8m3f-g62j-3vx8
CVE: CVE-2021-4287
CWE: CWE-59, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-8m3f-g62j-3vx8
Type: github-advisory

## Affected
- PyPI: `binwalk` — affected >=0 <2.3.3

## Details
A vulnerability, which was classified as problematic, was found in ReFirm Labs binwalk up to 2.3.2. Affected is an unknown function of the file src/binwalk/modules/extractor.py of the component Archive Extraction Handler. The manipulation leads to symlink following. It is possible to launch the attack remotely. Upgrading to version 2.3.3 can address this issue. The name of the patch is fa0c0bd59b8588814756942fe4cb5452e76c1dcd. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216876.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4287
- https://github.com/ReFirmLabs/binwalk/pull/556
- https://github.com/ReFirmLabs/binwalk/commit/fa0c0bd59b8588814756942fe4cb5452e76c1dcd
- https://github.com/ReFirmLabs/binwalk
- https://github.com/ReFirmLabs/binwalk/releases/tag/v2.3.3
- https://vuldb.com/?ctiid.216876
- https://vuldb.com/?id.216876
