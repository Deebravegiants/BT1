# [H] CVE-2017-16651

## Summary
Severity: High
Advisory: CVE-2017-16651
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-09
Source: https://osv.dev/vulnerability/CVE-2017-16651
Type: osv

## Details
Roundcube Webmail before 1.1.10, 1.2.x before 1.2.7, and 1.3.x before 1.3.3 allows unauthorized access to arbitrary files on the host's filesystem, including configuration files, as exploited in the wild in November 2017. The attacker must be able to authenticate at the target system with a valid username/password as the attack requires an active session. The issue is related to file-based attachment plugins and _task=settings&_action=upload-display&_from=timezone requests.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-16651
- http://www.securityfocus.com/bid/101793
- https://lists.debian.org/debian-lts-announce/2017/11/msg00039.html
- https://github.com/roundcube/roundcubemail/releases/tag/1.1.10
- https://github.com/roundcube/roundcubemail/releases/tag/1.2.7
- https://github.com/roundcube/roundcubemail/releases/tag/1.3.3
- https://roundcube.net/news/2017/11/08/security-updates-1.3.3-1.2.7-and-1.1.10
- https://www.debian.org/security/2017/dsa-4030
- https://github.com/roundcube/roundcubemail/issues/6026
- http://packetstormsecurity.com/files/161226/Roundcube-Webmail-1.2-File-Disclosure.html
