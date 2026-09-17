# [H] CVE-2016-6855

## Summary
Severity: High
Advisory: CVE-2016-6855
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/CVE-2016-6855
Type: osv

## Details
Eye of GNOME (aka eog) 3.16.5, 3.17.x, 3.18.x before 3.18.3, 3.19.x, and 3.20.x before 3.20.4, when used with glib before 2.44.1, allow remote attackers to cause a denial of service (out-of-bounds write and crash) via vectors involving passing invalid UTF-8 to GMarkup.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JVINHHR6VJKXTYYMAYKN5GROKHVT4UKB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T6GFDHLNPUG7JHWM3QLXQNRA7NZGU2KI/
- https://www.exploit-db.com/exploits/40291/
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00021.html
- http://www.securityfocus.com/bid/92616
- http://www.ubuntu.com/usn/USN-3069-1
- https://git.gnome.org/browse/eog/plain/NEWS?h=3.16.5
- https://git.gnome.org/browse/eog/plain/NEWS?h=3.18.3
- https://git.gnome.org/browse/eog/plain/NEWS?h=3.20.4
- https://bugzilla.gnome.org/show_bug.cgi?id=770143
- https://git.gnome.org/browse/eog/commit/?id=e99a8c00f959652fe7c10e2fa5a3a7a5c25e6af4
- http://packetstormsecurity.com/files/138486/Gnome-Eye-Of-Gnome-3.10.2-Out-Of-Bounds-Write.html
