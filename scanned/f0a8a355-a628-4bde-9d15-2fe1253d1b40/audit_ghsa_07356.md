# [C] DIRAC is vulnerable to RCE in RequestManager due to eval on untrusted input

## Summary
Severity: Critical
Advisory: GHSA-9jpv-c7p4-997x
CVE: CVE-2026-45579
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-9jpv-c7p4-997x
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=6 <8.0.79
- PyPI: `DIRAC` — affected >=8.1.0a1 <9.0.22
- PyPI: `DIRAC` — affected >=9.1.0 <9.1.10

## Details
### Summary
An remote code execution vulnerability exists in RequestManager due to the use of eval on untrusted input that allows any authenticated user to run code/commands on the DIRAC server as the system user running the DIRAC services.

### Details
The export_getRequestCountersWeb function is callable by any authenticated user and just passes its parameters directly to the database instance:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/RequestManagementSystem/Service/ReqManagerHandler.py#L270

If the groupingAttribute string is unrecognised, `Request.` is prepended to it and the result is passed into an `eval()` call:
https://github.com/DIRACGrid/DIRAC/blob/f7e0a3ac153315030fb3520e8ca747f013758967/src/DIRAC/RequestManagementSystem/DB/RequestDB.py#L766-L776

By passing in a dunder string that is applicable to the Request object, it's possible to work back up to functions in the os module and trigger them to be called in the server context.

There are other uses of eval in ReqManager/RequestDB which may be equally accessible.

### Impact
This allows any authenticated user to run commands on the server, which allows a full compromise of the DIRAC system (they can read the local dirac.cfg, get database passwords and export all stored proxies and tokens). If local logging is used, they can also remove evidence of the exploit from the log (it leaves an exception printout in the RequestManager log when used).

### Patched versions:
https://pypi.org/project/DIRAC/8.0.79/
https://pypi.org/project/DIRAC/9.0.22/
https://pypi.org/project/DIRAC/9.1.10/

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-9jpv-c7p4-997x
- https://github.com/DIRACGrid/DIRAC
- https://pypi.org/project/DIRAC/8.0.79
- https://pypi.org/project/DIRAC/9.0.22
- https://pypi.org/project/DIRAC/9.1.10
