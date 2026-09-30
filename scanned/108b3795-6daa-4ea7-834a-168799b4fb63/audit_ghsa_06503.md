# [C] DIRAC is vulnerable to RCE in FileCatalog DatasetManager via SQL injection + eval

## Summary
Severity: Critical
Advisory: GHSA-m4m7-4cw8-62j6
CVE: CVE-2026-61667
CWE: CWE-89, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-m4m7-4cw8-62j6
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=6 <8.0.79
- PyPI: `DIRAC` — affected >=8.1.0a1 <9.0.22
- PyPI: `DIRAC` — affected >=9.1.0 <9.1.10

## Details
### Summary
The FileCatalog DatasetManager runs a query on the database and passes the result to eval. The SQL query contains an injection vulnerability which allows an authenticated user to control the parameter returned to the eval resulting in remote code execution.

### Details

The FileCatalog checkDataset function passes its datasets argument directly to the backend DB handler:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/DataManagementSystem/Service/FileCatalogHandler.py#L591-L593

Which in turn passes it to the __checkDataset function:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/DataManagementSystem/DB/FileCatalogComponents/DatasetManager/DatasetManager.py#L390

This uses an f-string to create a query without escaping, resulting in an SQL injection:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/DataManagementSystem/DB/FileCatalogComponents/DatasetManager/DatasetManager.py#L400-L402

The result (which is user controllable due to the SQL injection) is passed into eval almost immediately on return, leading to code execution:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/DataManagementSystem/DB/FileCatalogComponents/DatasetManager/DatasetManager.py#L409

There are other functions in the same file which use a similar pattern and would likely be exploitable in a similar way.

### Impact
This allows any authenticated user to run commands on the server, which allows a full compromise of the DIRAC system (they can read the local dirac.cfg, get database passwords and export all stored proxies and tokens). If local logging is used, they can also remove evidence of the exploit from the log.

### Patched versions:
https://pypi.org/project/DIRAC/8.0.79/
https://pypi.org/project/DIRAC/9.0.22/
https://pypi.org/project/DIRAC/9.1.10/

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-m4m7-4cw8-62j6
- https://github.com/DIRACGrid/DIRAC
- https://pypi.org/project/DIRAC/8.0.79
- https://pypi.org/project/DIRAC/9.0.22
- https://pypi.org/project/DIRAC/9.1.10
