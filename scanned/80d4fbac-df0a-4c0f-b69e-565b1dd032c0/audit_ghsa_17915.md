# [M] OMERO.web displays unecessary user information when requesting password reset

## Summary
Severity: Medium
Advisory: GHSA-gpmg-4x4g-mr5r
CVE: CVE-2025-54791
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-gpmg-4x4g-mr5r
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.29.2

## Details
### Background

If an error occurred when resetting a user's password using the ``Forgot Password`` option in OMERO.web, the error message displayed on the Web page can disclose information about the user.

### Impact
OMERO.web before 5.29.1

### Patches
User should upgrade to 5.29.2 or higher

### Workarounds
Disable the ``Forgot password`` option in OMERO.web using the ``omero.web.show_forgot_password`` configuration property[^1].

Thanks to Christopher Youd who reported the issue.

Open an issue in [omero-web](https://github.com/ome/omero-web)
Email us at [security@openmicroscopy.org](mailto:security@openmicroscopy.org)

[^1]: https://omero.readthedocs.io/en/stable/sysadmins/config.html#omero.web.show_forgot_password

## References
- https://github.com/ome/omero-web/security/advisories/GHSA-gpmg-4x4g-mr5r
- https://nvd.nist.gov/vuln/detail/CVE-2025-54791
- https://github.com/ome/omero-web/commit/8aa2789e8f759c73f1517abe9a0abd44e86644ad
- https://github.com/ome/omero-web
