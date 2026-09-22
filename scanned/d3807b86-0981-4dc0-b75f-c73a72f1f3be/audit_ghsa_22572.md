# [M] MoinMoin Insertion of Sensitive Information into Log File

## Summary
Severity: Medium
Advisory: GHSA-mxh8-xgq9-w782
CVE: CVE-2007-0902
CWE: CWE-532
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-mxh8-xgq9-w782
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=1.5.7 <1.5.8

## Details
An information leak was discovered in MoinMoin's debug reporting version 1.5.7, which could expose information about the versions of software running on the host system.  MoinMoin administrators can add "show_traceback=0" to their site configurations to disable debug tracebacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0902
- https://moinmo.in/MoinMoinRelease1.5/CHANGES
- http://osvdb.org/33173
- http://secunia.com/advisories/24138
- http://secunia.com/advisories/24244
- http://www.securityfocus.com/bid/22515
- http://www.ubuntu.com/usn/usn-423-1
