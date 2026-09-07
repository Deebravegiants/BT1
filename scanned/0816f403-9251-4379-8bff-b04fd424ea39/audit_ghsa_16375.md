# [M] Docassemble HTML and javascript injection

## Summary
Severity: Medium
Advisory: GHSA-pcfx-g2j2-f6f6
CVE: CVE-2024-27290
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-pcfx-g2j2-f6f6
Type: github-advisory

## Affected
- PyPI: `docassemble.webapp` — affected >=0 <1.4.97

## Details
### Impact
A user could type HTML into a field, including the field for the user's name, and then that HTML could be displayed on the screen as HTML. The HTML can also contain `<script>` tags allowing JavaScript to execute on the page.

### Patches
The vulnerability has been patched in version 1.4.97 of the master branch. The Docker image on docker.io has been patched.

### Workarounds
If upgrading is not possible, manually apply the changes of [4801ac7](https://github.com/jhpyle/docassemble/commit/4801ac7ff7c90df00ac09523077930cdb6dea2aa) and restart the server (e.g., by pressing Save on the Configuration screen).

### Credit

The vulnerability was discovered by Riyush Ghimire (@richighimi).

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [docassemble](https://github.com/jhpyle/docassemble/issues)
* Join the [Slack channel](https://join.slack.com/t/docassemble/shared_invite/zt-2cspzjo9j-YyE7SrLmi5muAvnPv~Bz~A)
* Email us at jhpyle@gmail.com

## References
- https://github.com/jhpyle/docassemble/security/advisories/GHSA-pcfx-g2j2-f6f6
- https://nvd.nist.gov/vuln/detail/CVE-2024-27290
- https://github.com/jhpyle/docassemble/commit/4801ac7ff7c90df00ac09523077930cdb6dea2aa
- https://github.com/jhpyle/docassemble
