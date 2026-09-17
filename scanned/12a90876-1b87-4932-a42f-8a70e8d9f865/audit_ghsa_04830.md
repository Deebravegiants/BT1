# [H] Galaxy NG: command injection vulnerability

## Summary
Severity: High
Advisory: GHSA-6hw7-j4jw-wpff
CVE: CVE-2026-12398
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-6hw7-j4jw-wpff
Type: github-advisory

## Affected
- PyPI: `galaxy-ng` — affected >=0

## Details
A command injection vulnerability was found in galaxy_ng. The do_git_checkout() function in the legacy role import API (v1) interpolates unsanitized git ref names (branch/tag names) into shell commands executed via subprocess.run() with shell=True. An authenticated user who controls a git repository can create a branch or tag with shell metacharacters in the name to achieve remote code execution on the pulp worker. The vulnerable endpoint is only reachable when GALAXY_ENABLE_LEGACY_ROLES is set to True, which is not the default configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12398
- https://access.redhat.com/security/cve/CVE-2026-12398
- https://bugzilla.redhat.com/show_bug.cgi?id=2489180
- https://github.com/ansible/galaxy_ng
