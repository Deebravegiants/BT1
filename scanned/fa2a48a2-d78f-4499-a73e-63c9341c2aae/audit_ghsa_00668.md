# [M] Remote Code Execution (RCE) Exploit on Cross Site Scripting (XSS) Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hm45-mgqm-gjm4
CVE: CVE-2020-26249
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-12-08
Source: https://github.com/advisories/GHSA-hm45-mgqm-gjm4
Type: github-advisory

## Affected
- PyPI: `red-dashboard` — affected >=0 <0.1.7a

## Details
### Impact
A RCE exploit has been discovered in the Red Discord Bot - Dashboard Webserver: this exploit allows Discord users with specially crafted Server names and Usernames/Nicknames to inject code into the webserver front-end code.  By abusing this exploit, it's possible to perform destructive actions and/or access sensitive information.

### Patches
This high severity exploit has been fixed on version `0.1.7a`.

### Workarounds
There are no workarounds, bot owners must upgrade their relevant packages (Dashboard module and Dashboard webserver) in order to patch this issue

### References
- 99d88b8
- a6b9785

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Cog-Creators/Red-Dashboard](https://github.com/Cog-Creators/Red-Dashboard/issues/new/choose)
* Over on the official [Red Server](https://discord.gg/red) or at the Third Party Server [Toxic Layer](https://discord.gg/vQZTdB9)

## References
- https://github.com/Cog-Creators/Red-Dashboard/security/advisories/GHSA-hm45-mgqm-gjm4
- https://nvd.nist.gov/vuln/detail/CVE-2020-26249
- https://github.com/Cog-Creators/Red-Dashboard/commit/99d88b840674674166ce005b784ae8e31e955ab1
- https://github.com/Cog-Creators/Red-Dashboard/commit/a6b9785338003ec87fb75305e7d1cc2d40c7ab91
- https://github.com/Cog-Creators/Red-Dashboard
- https://github.com/pypa/advisory-database/tree/main/vulns/red-dashboard/PYSEC-2020-98.yaml
- https://pypi.org/project/Red-Dashboard
