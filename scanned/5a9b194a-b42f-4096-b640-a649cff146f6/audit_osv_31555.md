# [H] GIMP XCF File Parsing Use-After-Free Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-14424
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-14424
Type: osv

## Details
GIMP XCF File Parsing Use-After-Free Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GIMP. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of XCF files. The issue results from the lack of validating the existence of an object prior to performing operations on the object. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28376.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14424.json
- https://gitlab.gnome.org/GNOME/gimp/-/commit/5cc55d078b7fba995cef77d195fac325ee288ddd
- https://nvd.nist.gov/vuln/detail/CVE-2025-14424
- https://www.zerodayinitiative.com/advisories/ZDI-25-1138/
