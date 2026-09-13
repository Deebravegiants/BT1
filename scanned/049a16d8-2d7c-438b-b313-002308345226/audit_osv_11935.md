# [H] CVE-2018-1000135

## Summary
Severity: High
Advisory: CVE-2018-1000135
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-1000135
Type: osv

## Details
GNOME NetworkManager version 1.10.2 and earlier contains a Information Exposure (CWE-200) vulnerability in DNS resolver that can result in Private DNS queries leaked to local network's DNS servers, while on VPN. This vulnerability appears to have been fixed in Some Ubuntu 16.04 packages were fixed, but later updates removed the fix. cf. https://bugs.launchpad.net/ubuntu/+bug/1754671 an upstream fix does not appear to be available at this time.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00005.html
- http://www.securityfocus.com/bid/103478
- https://bugs.launchpad.net/ubuntu/+source/network-manager/+bug/1754671
- https://bugzilla.gnome.org/show_bug.cgi?id=746422
- https://bugzilla.redhat.com/show_bug.cgi?id=1553634
