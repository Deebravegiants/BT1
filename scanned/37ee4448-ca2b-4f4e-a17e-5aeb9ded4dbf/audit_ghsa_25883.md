# [M] Command injection in guake

## Summary
Severity: Medium
Advisory: GHSA-7x48-7466-3g33
CVE: CVE-2021-23556
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-7x48-7466-3g33
Type: github-advisory

## Affected
- PyPI: `guake` — affected >=0 <3.8.5

## Details
Guake is a drop-down terminal for GNOME. The package guake before 3.8.5 is vulnerable to Exposed Dangerous Method or Function due to the exposure of execute_command and execute_command_by_uuid methods via the d-bus interface, which makes it possible for a malicious user to run an arbitrary command via the d-bus method. **Note:** Exploitation requires the user to have installed another malicious program that will be able to send dbus signals or run terminal commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23556
- https://github.com/Guake/guake/issues/1796
- https://github.com/Guake/guake/pull/2017
- https://github.com/Guake/guake/commit/b769b3a5fd71a107c58679d217cccc971b4196b4
- https://github.com/Guake/guake
- https://github.com/Guake/guake/releases
- https://github.com/advisories/GHSA-7x48-7466-3g33
- https://github.com/pypa/advisory-database/tree/main/vulns/guake/PYSEC-2022-165.yaml
- https://snyk.io/vuln/SNYK-PYTHON-GUAKE-2386334
