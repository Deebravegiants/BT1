# [H] CVE-2010-4168

## Summary
Severity: High
Advisory: CVE-2010-4168
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2010-11-17
Source: https://osv.dev/vulnerability/CVE-2010-4168
Type: osv

## Details
Multiple use-after-free vulnerabilities in OpenTTD 1.0.x before 1.0.5 allow (1) remote attackers to cause a denial of service (invalid write and daemon crash) by abruptly disconnecting during transmission of the map from the server, related to network/network_server.cpp; (2) remote attackers to cause a denial of service (invalid read and daemon crash) by abruptly disconnecting, related to network/network_server.cpp; and (3) remote servers to cause a denial of service (invalid read and application crash) by forcing a disconnection during the join process, related to network/network.cpp.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/052187.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/052193.html
- http://secunia.com/advisories/42578
- http://security.openttd.org/en/CVE-2010-4168
- http://www.securityfocus.com/bid/44844
- http://www.vupen.com/english/advisories/2010/2985
- http://www.vupen.com/english/advisories/2010/3199
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/052187.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/052193.html
- http://marc.info/?l=oss-security&m=128975491407670&w=2
- http://marc.info/?l=oss-security&m=128984298802678&w=2
- http://security.openttd.org/en/CVE-2010-4168
- http://security.openttd.org/en/patch/28.patch
- http://vcs.openttd.org/svn/changeset/21182
- http://www.securityfocus.com/bid/44844
