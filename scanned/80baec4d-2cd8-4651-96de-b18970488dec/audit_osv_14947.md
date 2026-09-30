# [C] CVE-2019-12523

## Summary
Severity: Critical
Advisory: CVE-2019-12523
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-12523
Type: osv

## Details
An issue was discovered in Squid before 4.9. When handling a URN request, a corresponding HTTP request is made. This HTTP request doesn't go through the access checks that incoming HTTP requests go through. This causes all access checks to be bypassed and allows access to restricted HTTP servers, e.g., an attacker can connect to HTTP servers that only listen on localhost.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00056.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_8.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://usn.ubuntu.com/4213-1/
- https://usn.ubuntu.com/4446-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156329
