# [C] Arbitrary Code Execution via Unsafe Deserialization in LabOne Q

## Summary
Severity: Critical
Advisory: CVE-2026-7584
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-7584
Type: osv

## Details
The LabOne Q serialization framework uses a class-loading mechanism (import_cls) to dynamically import and instantiate Python classes during deserialization. Prior to the fix, this mechanism accepted arbitrary fully-qualified class names from the serialized data without any validation of the target class or restriction on which modules could be imported. An attacker can craft a serialized experiment file that causes the deserialization engine to import and instantiate arbitrary Python classes with attacker-controlled constructor arguments, resulting in arbitrary code execution in the context of the user running the Python process. Exploitation requires the victim to load a malicious file using LabOne Q's deserialization functions, for example a compromised experiment file shared for collaboration or support purposes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7584
- https://www.zhinst.com/support/security/2026/zi-sa-2026-002/
- https://pypi.org/project/laboneq/
