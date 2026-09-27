# [M] compliance-trestle Vulnerable to SSRF in Remote Fetching Subsystem

## Summary
Severity: Medium
Advisory: GHSA-w76h-q7c6-jpjp
CVE: CVE-2026-46380
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-w76h-q7c6-jpjp
Type: github-advisory

## Affected
- PyPI: `compliance-trestle` — affected >=4.0.0 <4.0.3
- PyPI: `compliance-trestle` — affected >=0 <3.12.2

## Details
A source code audit led to the discovery of three significant security vulnerabilities in the trestle/core/remote/cache.py module.

**Finding 1 (Critical): SSRF (CWE-918)**
The HTTPSFetcher._do_fetch() method passes a user-supplied URL directly to requests.get() without validation. This allows an attacker to perform Server-Side Request Forgery, targeting internal services or cloud metadata endpoints (e.g., 169.254.169.254).

Per [rule 4.2.11 of the CVE CNA rules](https://www.cve.org/ResourcesSupport/AllResources/CNARules#section_4-2_CVE_ID_Assignment) Finding 1 will be addressed in this advisory, while findings 2 & 3 will be addressed in separate advisories:

---

Multiple Path Traversal Vulnerabilities in Remote Fetching Subsystem

**Finding 2 & 3 (High/Medium): Path Traversal (CWE-22)**
The caching logic for HTTPSFetcher and LocalFetcher fails to sanitize URI paths, allowing for arbitrary file reads via file:// or writing cached files outside the intended directory.

Impact: > These vulnerabilities can be chained to exfiltrate sensitive cloud credentials or compromise CI/CD environments.

Reproduction: > Please see the attached poc_ssrf_and_path_traversal.py and terminal_output.txt. 13 exploit vectors have been verified locally.

[compliance-trestle_audit_2026-03-30.pdf](https://github.com/user-attachments/files/26348930/compliance-trestle_audit_2026-03-30.pdf)
[poc_ssrf_and_path_traversal.py](https://github.com/user-attachments/files/26348820/poc_ssrf_and_path_traversal.py)
[terminal_output.txt](https://github.com/user-attachments/files/26348821/terminal_output.txt)

## References
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-w76h-q7c6-jpjp
- https://github.com/oscal-compass/compliance-trestle/commit/53de5e75332888ea54f5da41d4c7859bb1d608e1
- https://github.com/oscal-compass/compliance-trestle/commit/5c65c5926fe7ca908b9c1d281f904e7d97ba8310
- https://github.com/oscal-compass/compliance-trestle
