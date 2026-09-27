# [H] Docassemble unauthorized access through URL manipulation

## Summary
Severity: High
Advisory: GHSA-jq57-3w7p-vwvv
CVE: CVE-2024-27292
CWE: CWE-706
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-jq57-3w7p-vwvv
Type: github-advisory

## Affected
- PyPI: `docassemble.webapp` — affected >=1.4.53 <1.4.97
- PyPI: `docassemble.base` — affected >=1.4.53 <1.4.97

## Details
### Impact
The vulnerability allows attackers to gain unauthorized access to information on the system through URL manipulation. It affects versions 1.4.53 to 1.4.96.

### Patches
The vulnerability has been patched in version 1.4.97 of the master branch. The Docker image on docker.io has been patched.

### Workarounds
If upgrading is not possible, manually apply the changes of [97f77dc](https://github.com/jhpyle/docassemble/commit/97f77dc486a26a22ba804765bfd7058aabd600c9) and restart the server.

### Credit

The vulnerability was discovered by Riyush Ghimire (@richighimi).

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [docassemble](https://github.com/jhpyle/docassemble/issues)
* Join the [Slack channel](https://join.slack.com/t/docassemble/shared_invite/zt-2cspzjo9j-YyE7SrLmi5muAvnPv~Bz~A)
* Email us at jhpyle@gmail.com

## References
- https://github.com/jhpyle/docassemble/security/advisories/GHSA-jq57-3w7p-vwvv
- https://nvd.nist.gov/vuln/detail/CVE-2024-27292
- https://github.com/jhpyle/docassemble/commit/97f77dc486a26a22ba804765bfd7058aabd600c9
- https://github.com/jhpyle/docassemble
