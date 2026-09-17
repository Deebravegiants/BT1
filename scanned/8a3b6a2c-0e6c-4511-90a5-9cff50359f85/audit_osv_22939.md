# [C] CVE-2022-41352

## Summary
Severity: Critical
Advisory: CVE-2022-41352
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-41352
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 8.8.15 and 9.0. An attacker can upload arbitrary files through amavis via a cpio loophole (extraction to /opt/zimbra/jetty/webapps/zimbra/public) that can lead to incorrect access to any other user accounts. Zimbra recommends pax over cpio. Also, pax is in the prerequisites of Zimbra on Ubuntu; however, pax is no longer part of a default Red Hat installation after RHEL 6 (or CentOS 6). Once pax is installed, amavis automatically prefers it over cpio.

## References
- http://packetstormsecurity.com/files/169458/Zimbra-Collaboration-Suite-TAR-Path-Traversal.html
- https://forums.zimbra.org/viewtopic.php?t=71153&p=306532
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-41352
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41352.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41352
- https://www.secpod.com/blog/unpatched-rce-bug-in-zimbra-collaboration-suite-exploited-in-wild/
