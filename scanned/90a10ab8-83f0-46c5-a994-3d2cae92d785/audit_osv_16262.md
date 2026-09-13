# [H] CVE-2019-3842

## Summary
Severity: High
Advisory: CVE-2019-3842
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-3842
Type: osv

## Details
In systemd before v242-rc4, it was discovered that pam_systemd does not properly sanitize the environment before using the XDG_SEAT variable. It is possible for an attacker, in some particular configurations, to set a XDG_SEAT environment variable which allows for commands to be checked against polkit policies using the "allow_active" element rather than "allow_any".

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/STR36RJE4ZZIORMDXRERVBHMPRNRTHAC/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00062.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3842
- http://packetstormsecurity.com/files/152610/systemd-Seat-Verification-Active-Session-Spoofing.html
- https://www.exploit-db.com/exploits/46743/
