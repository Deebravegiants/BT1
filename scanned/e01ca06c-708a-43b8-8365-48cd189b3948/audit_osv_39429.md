# [H] Netatalk has Integer Underflow → Stack Buffer Overflow in deletedir()

## Summary
Severity: High
Advisory: CVE-2026-45698
Aliases: GHSA-5443-v9xg-mqgv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-45698
Type: osv

## Details
Netatalk is a Free and Open Source file server suite for Unix-like operating systems. In versions 3.1.19 through 4.4.2, a stack-based buffer overflow exists in the deletedir() function of Netatalk's afpd daemon due to an integer underflow in the calculation of the remaining buffer size used for path construction. deletedir() is a utility function called when a file operation crosses a device boundary inside an AFP shared volume, which the standard library's renameat() cannot handle. The function attempts to prevent buffer overflows by tracking available space in a size_t remain variable. However, the arithmetic used to compute remain results in an unsigned integer underflow, causing the variable to become SIZE_MAX. Because of this, the subsequent boundary check always evaluates as safe, allowing an unbounded strcpy() operation to copy attacker-controlled filenames into a nearly full stack buffer. Version 4.4.3 patches the issue.

## References
- https://github.com/Netatalk/netatalk/releases/tag/netatalk-4-4-3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45698.json
- https://github.com/Netatalk/netatalk/security/advisories/GHSA-5443-v9xg-mqgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45698
