# [C] CVE-2024-42330

## Summary
Severity: Critical
Advisory: CVE-2024-42330
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-42330
Type: osv

## Details
The HttpRequest object allows to get the HTTP headers from the server's response after sending the request. The problem is that the returned strings are created directly from the data returned by the server and are not correctly encoded for JavaScript. This allows to create internal strings that can be used to access hidden properties of objects.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00005.html
- https://support.zabbix.com/browse/ZBX-25626
