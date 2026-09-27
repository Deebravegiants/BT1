# [H] CVE-2019-20006

## Summary
Severity: High
Advisory: CVE-2019-20006
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-20006
Type: osv

## Details
An issue was discovered in ezXML 0.8.3 through 0.8.6. The function ezxml_char_content puts a pointer to the internal address of a larger block as xml->txt. This is later deallocated (using free), leading to a segmentation fault.

## References
- https://sourceforge.net/p/ezxml/bugs/15/
