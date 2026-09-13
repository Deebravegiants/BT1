# [C] qBittorrent Web UI Default Credentials Lead to RCE

## Summary
Severity: Critical
Advisory: CVE-2023-30801
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/CVE-2023-30801
Type: osv

## Details
All versions of the qBittorrent client through 4.5.5 use default credentials when the web user interface is enabled. The administrator is not forced to change the default credentials. As of 4.5.5, this issue has not been fixed. A remote attacker can use the default credentials to authenticate and execute arbitrary operating system commands using the "external program" feature in the web user interface. This was reportedly exploited in the wild in March 2023.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T5WXBKELVZFZNIDONIJESOCSRPIQNCGI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U4BNFJR3ZWVLE2YSYIQYBWVDQBBZOLEL/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30801.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30801
- https://vulncheck.com/advisories/qbittorrent-default-creds
- https://github.com/qbittorrent/qBittorrent/issues/18731
