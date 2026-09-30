# [H] CVE-2021-28040

## Summary
Severity: High
Advisory: CVE-2021-28040
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-28040
Type: osv

## Details
An issue was discovered in OSSEC 3.6.0. An uncontrolled recursion vulnerability in os_xml.c occurs when a large number of opening and closing XML tags is used. Because recursion is used in _ReadElem without restriction, an attacker can trigger a segmentation fault once unmapped memory is reached.

## References
- https://github.com/ossec/ossec-hids/issues/1953
