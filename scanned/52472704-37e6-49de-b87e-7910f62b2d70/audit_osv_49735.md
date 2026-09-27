# [H] CVE-2019-17637

## Summary
Severity: High
Advisory: CVE-2019-17637
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2019-17637
Type: osv

## Details
In all versions of Eclipse Web Tools Platform through release 3.18 (2020-06), XML and DTD files referring to external entities could be exploited to send the contents of local files to a remote server when edited or validated, even when external entity resolution is disabled in the user preferences.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00016.html
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=458571
