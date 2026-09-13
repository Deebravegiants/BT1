# [H] CVE-2019-10143

## Summary
Severity: High
Advisory: CVE-2019-10143
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/CVE-2019-10143
Type: osv

## Details
It was discovered freeradius up to and including version 3.0.19 does not correctly configure logrotate, allowing a local attacker who already has control of the radiusd user to escalate his privileges to root, by tricking logrotate into writing a radiusd-writable file to a directory normally inaccessible by the radiusd user. NOTE: the upstream software maintainer has stated "there is simply no way for anyone to gain privileges through this alleged issue."

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A6VKBZAZKJP5QKXDXRKCM2ZPZND3TFAX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TKODLHHUOVAYENTBP4D3N25ST3Q6LJBP/
- https://access.redhat.com/errata/RHSA-2019:3353
- https://freeradius.org/security/
- https://github.com/FreeRADIUS/freeradius-server/pull/2666
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10143
- http://packetstormsecurity.com/files/155361/FreeRadius-3.0.19-Logrotate-Privilege-Escalation.html
- http://seclists.org/fulldisclosure/2019/Nov/14
