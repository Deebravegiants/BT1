# [C] NLTK before 3.10.0 Remote Code Execution via Unsafe Pickle Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-78683
Aliases: GHSA-rhp5-r9x4-f5g2, PYSEC-2026-3734
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78683
Type: osv

## Details
NLTK before 3.10.0 (affected versions <=3.9.4) contains an unsafe pickle deserialization vulnerability in the TransitionParser.parse() method (nltk/parse/transitionparser.py). The method calls pickle_load() with the default restricted=False, routing deserialization through WarningUnpickler, which does not override find_class() and therefore permits arbitrary class resolution. When an application loads an attacker-crafted model file, embedded pickle gadget chains execute arbitrary Python code with the privileges of the user running the application. NLTK provides a RestrictedUnpickler for safe deserialization, but it is not used by production code paths. Fixed in 3.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78683.json
- https://github.com/nltk/nltk/security/advisories/GHSA-rhp5-r9x4-f5g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-78683
- https://www.vulncheck.com/advisories/nltk-before-remote-code-execution-via-unsafe-pickle-deserialization
