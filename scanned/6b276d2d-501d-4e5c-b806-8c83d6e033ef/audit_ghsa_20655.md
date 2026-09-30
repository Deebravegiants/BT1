# [H] Bots using py-cord as Discord API wrapper are vulnerable to shutdowns through remote code execution

## Summary
Severity: High
Advisory: GHSA-qmhj-m29v-gvmr
CVE: CVE-2022-36024
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-qmhj-m29v-gvmr
Type: github-advisory

## Affected
- PyPI: `py-cord` — affected >=2.0.0 <2.0.1

## Details
### Impact
py-cord is a an API wrapper for Discord written in Python. Bots using py-cord version 2.0.0 are vulnerable to remote shutdown if they are added to the server with the `application.commands` scope without the `bot` scope. Currently, it appears that all public bots that use slash commands are affected.

### Patches
This issue has been patched in version 2.0.1.

### Workarounds
There are currently no recommended workarounds - please upgrade to a patched version.

### References
https://github.com/Pycord-Development/pycord/pull/1568

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [our GitHub](https://github.com/Pycord-Development/pycord)
* Email us at [support@pycord.dev](mailto:support@pycord.dev)

## References
- https://github.com/Pycord-Development/pycord/security/advisories/GHSA-qmhj-m29v-gvmr
- https://nvd.nist.gov/vuln/detail/CVE-2022-36024
- https://github.com/Pycord-Development/pycord/pull/1568
- https://github.com/Pycord-Development/pycord
- https://github.com/pypa/advisory-database/tree/main/vulns/py-cord/PYSEC-2022-43146.yaml
