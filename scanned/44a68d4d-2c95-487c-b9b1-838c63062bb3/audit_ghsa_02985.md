# [M] ReDoS in LDAP schema parser

## Summary
Severity: Medium
Advisory: GHSA-r8wq-qrxc-hmcm
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-29
Source: https://github.com/advisories/GHSA-r8wq-qrxc-hmcm
Type: github-advisory

## Affected
- PyPI: `python-ldap` — affected >=0 <3.4.0

## Details
https://github.com/python-ldap/python-ldap/issues/424

### Impact
The LDAP schema parser of python-ldap 3.3.1 and earlier are vulnerable to a regular expression denial-of-service attack. The issue affects clients that use ``ldap.schema`` package to parse LDAP schema definitions from an untrusted source.

### Patches
The upcoming release of python-ldap 3.4.0 will contain a workaround to prevent ReDoS attacks. The schema parser refuses schema definitions with an excessive amount of backslashes.

### Workarounds
As a workaround, users can check input for excessive amount of backslashes in schemas. More than a dozen backslashes per line are atypical.

### References
[CWE-1333](https://cwe.mitre.org/data/definitions/1333.html)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [python-ldap](https://github.com/python-ldap/python-ldap) tracker

## References
- https://github.com/python-ldap/python-ldap/security/advisories/GHSA-r8wq-qrxc-hmcm
- https://github.com/python-ldap/python-ldap/issues/424
- https://github.com/python-ldap/python-ldap
