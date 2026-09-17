# [H] CVE-2016-4021

## Summary
Severity: High
Advisory: CVE-2016-4021
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-26
Source: https://osv.dev/vulnerability/CVE-2016-4021
Type: osv

## Details
The read_binary function in buffer.c in pgpdump before 0.30 allows context-dependent attackers to cause a denial of service (infinite loop and CPU consumption) via crafted input, as demonstrated by the \xa3\x03 string.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183750.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184617.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184689.html
- https://github.com/kazu-yamamoto/pgpdump/pull/16
- http://seclists.org/bugtraq/2016/Apr/99
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2016-030.txt
