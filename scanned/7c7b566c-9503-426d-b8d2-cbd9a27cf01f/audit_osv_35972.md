# [H] Aeon load_human_activity_segmentation_datasets Code Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-18286
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-18286
Type: osv

## Details
Aeon load_human_activity_segmentation_datasets Code Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of aeon. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the load_human_activity_segmentation_datasets method. The issue results from the lack of proper validation of a user-supplied string before using it to execute Python code. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-29160.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18286.json
- https://github.com/aeon-toolkit/aeon/commit/751918052c0cce266b4f7cd4b084408526efc015
- https://nvd.nist.gov/vuln/detail/CVE-2026-18286
- https://www.zerodayinitiative.com/advisories/ZDI-26-469/
