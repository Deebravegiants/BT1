# [H] CVE-2015-8612

## Summary
Severity: High
Advisory: CVE-2015-8612
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-8612
Type: osv

## Details
The EnableNetwork method in the Network class in plugins/mechanism/Network.py in Blueman before 2.0.3 allows local users to gain privileges via the dhcp_handler argument.

## References
- http://www.debian.org/security/2015/dsa-3427
- https://github.com/blueman-project/blueman/issues/416
- http://packetstormsecurity.com/files/135047/Slackware-Security-Advisory-blueman-Updates.html
- http://www.openwall.com/lists/oss-security/2015/12/18/6
- http://www.openwall.com/lists/oss-security/2015/12/19/1
- http://www.securityfocus.com/bid/79688
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2015&m=slackware-security.421085
- https://github.com/blueman-project/blueman/releases/tag/2.0.3
- https://twitter.com/thegrugq/status/677809527882813440
- https://www.exploit-db.com/exploits/46186/
