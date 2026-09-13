# [M] CVE-2019-15162

## Summary
Severity: Medium
Advisory: CVE-2019-15162
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/CVE-2019-15162
Type: osv

## Details
rpcapd/daemon.c in libpcap before 1.9.1 on non-Windows platforms provides details about why authentication failed, which might make it easier for attackers to enumerate valid usernames.

## References
- http://seclists.org/fulldisclosure/2019/Dec/26
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5P5K3DQ4TFSZBDB3XN4CZNJNQ3UIF3D3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GBIEKWLNIR62KZ5GA7EDXZS52HU6OE5F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UZTIPUWABYUE5KQOLCKAW65AUUSB7QO6/
- https://seclists.org/bugtraq/2019/Dec/23
- https://support.apple.com/kb/HT210785
- https://support.apple.com/kb/HT210788
- https://support.apple.com/kb/HT210789
- https://support.apple.com/kb/HT210790
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://github.com/the-tcpdump-group/libpcap/blob/libpcap-1.9/CHANGES
- https://www.tcpdump.org/public-cve-list.txt
- https://github.com/the-tcpdump-group/libpcap/commit/484d60cbf7ca4ec758c3cbb8a82d68b244a78d58
