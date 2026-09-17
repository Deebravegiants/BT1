# [H] CVE-2023-1668

## Summary
Severity: High
Advisory: CVE-2023-1668
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-04-10
Source: https://osv.dev/vulnerability/CVE-2023-1668
Type: osv

## Details
A flaw was found in openvswitch (OVS). When processing an IP packet with protocol 0, OVS will install the datapath flow without the action modifying the IP header. This issue results (for both kernel and userspace datapath) in installing a datapath flow matching all IP protocols (nw_proto is wildcarded) for this flow, but with an incorrect action, possibly causing incorrect handling of other IP packets with a != 0 IP protocol that matches this dp flow.

## References
- https://www.openwall.com/lists/oss-security/2023/04/06/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1668.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2GUNS3WSJG4TUDKZ5L7FXGJMVOD6EJZ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1668
- https://security.gentoo.org/glsa/202311-16
- https://www.debian.org/security/2023/dsa-5387
- https://bugzilla.redhat.com/show_bug.cgi?id=2137666
- https://lists.debian.org/debian-lts-announce/2023/05/msg00000.html
