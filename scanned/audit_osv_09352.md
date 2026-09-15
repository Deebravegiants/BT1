# [H] CVE-2016-9566

## Summary
Severity: High
Advisory: CVE-2016-9566
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-15
Source: https://osv.dev/vulnerability/CVE-2016-9566
Type: osv

## Details
base/logging.c in Nagios Core before 4.2.4 allows local users with access to an account in the nagios group to gain root privileges via a symlink attack on the log file.  NOTE: this can be leveraged by remote attackers using CVE-2016-9565.

## References
- http://www.securitytracker.com/id/1037487
- https://lists.debian.org/debian-lts-announce/2018/12/msg00014.html
- https://www.exploit-db.com/exploits/40921/
- http://rhn.redhat.com/errata/RHSA-2017-0211.html
- http://rhn.redhat.com/errata/RHSA-2017-0212.html
- http://rhn.redhat.com/errata/RHSA-2017-0213.html
- http://rhn.redhat.com/errata/RHSA-2017-0214.html
- http://rhn.redhat.com/errata/RHSA-2017-0258.html
- http://rhn.redhat.com/errata/RHSA-2017-0259.html
- http://seclists.org/fulldisclosure/2016/Dec/58
- http://www.securityfocus.com/bid/94919
- https://security.gentoo.org/glsa/201612-51
- https://security.gentoo.org/glsa/201702-26
- https://security.gentoo.org/glsa/201710-20
- https://www.nagios.org/projects/nagios-core/history/4x/
- https://bugzilla.redhat.com/show_bug.cgi?id=1402869
- https://github.com/NagiosEnterprises/nagioscore/commit/c29557dec91eba2306f5fb11b8da4474ba63f8c4
- https://legalhackers.com/advisories/Nagios-Exploit-Root-PrivEsc-CVE-2016-9566.html
