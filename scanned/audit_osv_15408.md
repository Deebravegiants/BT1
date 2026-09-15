# [H] CVE-2019-15903

## Summary
Severity: High
Advisory: CVE-2019-15903
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15903
Type: osv

## Details
In libexpat before 2.2.8, crafted XML input could fool the parser into changing from DTD parsing to document parsing too early; a consecutive call to XML_GetCurrentLineNumber (or XML_GetCurrentColumnNumber) then resulted in a heap-based buffer over-read.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A4TZKPJFTURRLXIGLB34WVKQ5HGY6JJA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BDUTI5TVQWIGGQXPEVI4T2ENHFSBMIBP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S26LGXXQ7YF2BP3RGOWELBFKM6BHF6UG/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00081.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- http://packetstormsecurity.com/files/154503/Slackware-Security-Advisory-expat-Updates.html
- http://packetstormsecurity.com/files/154927/Slackware-Security-Advisory-python-Updates.html
- http://packetstormsecurity.com/files/154947/Slackware-Security-Advisory-mozilla-firefox-Updates.html
- http://seclists.org/fulldisclosure/2019/Dec/23
- http://seclists.org/fulldisclosure/2019/Dec/26
