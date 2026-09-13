# [H] CVE-2019-15163

## Summary
Severity: High
Advisory: CVE-2019-15163
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/CVE-2019-15163
Type: osv

## Details
rpcapd/daemon.c in libpcap before 1.9.1 allows attackers to cause a denial of service (NULL pointer dereference and daemon crash) if a crypt() call fails.

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
- https://support.f5.com/csp/article/K92862401?utm_source=f5support&amp%3Butm_medium=RSS
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://github.com/the-tcpdump-group/libpcap/blob/libpcap-1.9/CHANGES
- https://www.tcpdump.org/public-cve-list.txt
- https://github.com/the-tcpdump-group/libpcap/commit/437b273761adedcbd880f714bfa44afeec186a31
