# [H] In libexpat before 2.2.8, crafted XML input could fool the parser into changing from DTD parsing to...

## Summary
Severity: High
Advisory: JLSEC-2025-41
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-41
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.2.10+0

## Details
In libexpat before 2.2.8, crafted XML input could fool the parser into changing from DTD parsing to document parsing too early; a consecutive call to `XML_GetCurrentLineNumber` (or `XML_GetCurrentColumnNumber`) then resulted in a heap-based buffer over-read.

## References
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
- http://seclists.org/fulldisclosure/2019/Dec/27
- http://seclists.org/fulldisclosure/2019/Dec/30
- https://access.redhat.com/errata/RHSA-2019:3210
