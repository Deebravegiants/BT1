# [H] DIRAC: SQL injection and lack of access control in PilotManager service

## Summary
Severity: High
Advisory: GHSA-7xw9-549r-8jrc
CWE: CWE-284, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-7xw9-549r-8jrc
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=6 <8.0.79
- PyPI: `DIRAC` — affected >=8.1.0a1 <9.0.22
- PyPI: `DIRAC` — affected >=9.1.0 <9.1.10

## Details
### Details
A number of the functions in PilotManager pass parameters directly through to the database layer, which then does not do any escaping on the parameters. For example setPilotStatus:
https://github.com/DIRACGrid/DIRAC/blob/1738e7c6d2f31d26f1364255d9d2e87b4896c922/src/DIRAC/WorkloadManagementSystem/Service/PilotManagerHandler.py#L343-L349

https://github.com/DIRACGrid/DIRAC/blob/1738e7c6d2f31d26f1364255d9d2e87b4896c922/src/DIRAC/WorkloadManagementSystem/DB/PilotAgentsDB.py#L117

This won't accept multiple statements separated by a semicolon, but a carefully crafted set of parameters containing SQL escapes would likely be able to change or return other database entries.

Further to this, the PilotManager access control is only set to "authenticated"; this allows these functions to be called by any user. This allows any user to manage (e.g. delete, read output of) any pilot pilot job:
https://github.com/DIRACGrid/DIRAC/blob/1738e7c6d2f31d26f1364255d9d2e87b4896c922/src/DIRAC/WorkloadManagementSystem/ConfigTemplate.cfg#L111-L118

This is fixed by changing the SQL statements to use proper parameter substitution and providing a suitable set of access rules for the exported pilot management functions.

### Patched versions:
https://pypi.org/project/DIRAC/8.0.79/
https://pypi.org/project/DIRAC/9.0.22/
https://pypi.org/project/DIRAC/9.1.10/

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-7xw9-549r-8jrc
- https://github.com/DIRACGrid/DIRAC
- https://pypi.org/project/DIRAC/8.0.79
- https://pypi.org/project/DIRAC/9.0.22
- https://pypi.org/project/DIRAC/9.1.10
