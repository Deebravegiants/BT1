# [C] CVE-2025-23016

## Summary
Severity: Critical
Advisory: CVE-2025-23016
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-10
Source: https://osv.dev/vulnerability/CVE-2025-23016
Type: osv

## Details
FastCGI fcgi2 (aka fcgi) 2.x through 2.4.4 has an integer overflow (and resultant heap-based buffer overflow) via crafted nameLen or valueLen values in data to the IPC socket. This occurs in ReadParams in fcgiapp.c.

## References
- http://www.openwall.com/lists/oss-security/2025/04/23/4
- https://github.com/FastCGI-Archives/fcgi2/releases/tag/2.4.5
- https://lists.debian.org/debian-lts-announce/2025/10/msg00009.html
- https://www.synacktiv.com/en/publications/cve-2025-23016-exploiting-the-fastcgi-library
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23016.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23016
- https://github.com/FastCGI-Archives/fcgi2/issues/67
