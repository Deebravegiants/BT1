# [C] CVE-2017-12791

## Summary
Severity: Critical
Advisory: CVE-2017-12791
Aliases: GHSA-xxvj-8g5m-4qgw, PYSEC-2017-35
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-12791
Type: osv

## Details
Directory traversal vulnerability in minion id validation in SaltStack Salt before 2016.11.7 and 2017.7.x before 2017.7.1 allows remote minions with incorrect credentials to authenticate to a master via a crafted minion ID.

## References
- http://www.securityfocus.com/bid/100384
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=872399
- https://bugzilla.redhat.com/show_bug.cgi?id=1482006
- https://docs.saltstack.com/en/2016.11/topics/releases/2016.11.7.html
- https://docs.saltstack.com/en/latest/topics/releases/2017.7.1.html
- https://github.com/saltstack/salt/pull/42944
