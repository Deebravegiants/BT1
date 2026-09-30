# [H] CVE-2019-3871

## Summary
Severity: High
Advisory: CVE-2019-3871
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-3871
Type: osv

## Details
A vulnerability was found in PowerDNS Authoritative Server before 4.0.7 and before 4.1.7. An insufficient validation of data coming from the user when building a HTTP request from a DNS query in the HTTP Connector of the Remote backend, allowing a remote user to cause a denial of service by making the server connect to an invalid endpoint, or possibly information disclosure by making the server connect to an internal endpoint and somehow extracting meaningful information about the response

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00022.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GWUHF6MRSQ3YO7UUISGLV7MXCAGBW2VD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ROFI6OTWF4GKONNSNEDUCW6LVSSEBZNF/
- https://seclists.org/bugtraq/2019/Apr/8
- http://www.securityfocus.com/bid/107491
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2019-03.html
- https://www.debian.org/security/2019/dsa-4424
- http://www.openwall.com/lists/oss-security/2019/03/18/4
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3871
