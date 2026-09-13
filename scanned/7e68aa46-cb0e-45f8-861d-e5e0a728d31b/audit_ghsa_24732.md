# [H] Saltstack Salt Unauthenticated Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-pmj6-9f8c-8g2m
CVE: CVE-2021-25315
CWE: CWE-287, CWE-303
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pmj6-9f8c-8g2m
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3002.2

## Details
A Incorrect Implementation of Authentication Algorithm vulnerability in of SUSE SUSE Linux Enterprise Server 15 SP 3; openSUSE Tumbleweed allows local attackers to execute arbitrary code via salt without the need to specify valid credentials. This issue affects: SUSE SUSE Linux Enterprise Server 15 SP 3 salt versions prior to 3002.2-3. openSUSE Tumbleweed salt version 3002.2-2.1 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25315
- https://bugzilla.suse.com/show_bug.cgi?id=1182382
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2021-891.yaml
- https://github.com/saltstack/salt
