# [H] GIMP ILBM File Parsing Stack-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-10925
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-29
Source: https://osv.dev/vulnerability/CVE-2025-10925
Type: osv

## Details
GIMP ILBM File Parsing Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GIMP. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of ILBM files. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-27793.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10925.json
- https://gitlab.gnome.org/GNOME/gimp/-/merge_requests/2450
- https://nvd.nist.gov/vuln/detail/CVE-2025-10925
- https://www.zerodayinitiative.com/advisories/ZDI-25-914/
