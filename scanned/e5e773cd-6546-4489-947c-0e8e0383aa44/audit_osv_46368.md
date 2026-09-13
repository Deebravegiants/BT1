# [H] CVE-2006-20001

## Summary
Severity: High
Advisory: CVE-2006-20001
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2006-20001
Type: osv

## Details
A carefully crafted If: request header can cause a memory read, or write of a single zero byte, in a pool (heap) memory location beyond the header value sent. This could cause the process to crash.

This issue affects Apache HTTP Server 2.4.54 and earlier.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.gentoo.org/glsa/202309-01
- https://security.netapp.com/advisory/ntap-20230316-0005/
