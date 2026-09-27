# [C] CVE-2015-8954

## Summary
Severity: Critical
Advisory: CVE-2015-8954
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2015-8954
Type: osv

## Details
The MemcmpLowercase function in Suricata before 2.0.6 improperly excludes the first byte from comparisons, which might allow remote attackers to bypass intrusion-prevention functionality via a crafted HTTP request.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=777523
- https://redmine.openinfosecfoundation.org/issues/1364
- https://suricata-ids.org/2015/01/15/suricata-2-0-6-available/
