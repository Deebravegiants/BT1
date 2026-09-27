# [H] CVE-2018-15687

## Summary
Severity: High
Advisory: CVE-2018-15687
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-15687
Type: osv

## Details
A race condition in chown_one() of systemd allows an attacker to cause systemd to set arbitrary permissions on arbitrary files. Affected releases are systemd versions up to and including 239.

## References
- http://www.securityfocus.com/bid/105748
- https://security.gentoo.org/glsa/201810-10
- https://usn.ubuntu.com/3816-1/
- https://github.com/systemd/systemd/pull/10517/commits
- https://www.exploit-db.com/exploits/45715/
