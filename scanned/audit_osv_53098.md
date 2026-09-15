# [H] CVE-2022-28734

## Summary
Severity: High
Advisory: CVE-2022-28734
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-28734
Type: osv

## Details
Out-of-bounds write when handling split HTTP headers; When handling split HTTP headers, GRUB2 HTTP code accidentally moves its internal data buffer point by one position. This can lead to a out-of-bound write further when parsing the HTTP request, writing a NULL byte past the buffer. It's conceivable that an attacker controlled set of packets can lead to corruption of the GRUB2's internal memory metadata.

## References
- https://security.netapp.com/advisory/ntap-20230825-0002/
- https://www.openwall.com/lists/oss-security/2022/06/07/5
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-28734
