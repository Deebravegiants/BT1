# [M] CVE-2016-1000110

## Summary
Severity: Medium
Advisory: CVE-2016-1000110
Aliases: PSF-2019-2
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2016-1000110
Type: osv

## Details
The CGIHandler class in Python before 2.7.12 does not protect against the HTTP_PROXY variable name clash in a CGI script, which could allow a remote attacker to redirect HTTP requests.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7K3WFJO3SJQCODKRKU6EQV3ZGHH53YPU/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://security-tracker.debian.org/tracker/CVE-2016-1000110
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-1000110
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2016-1000110
