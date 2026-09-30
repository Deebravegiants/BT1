# [H] Openvswsitch: ovs-vswitch fails to recover after malformed geneve metadata packet

## Summary
Severity: High
Advisory: CVE-2023-3966
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-3966
Type: osv

## Details
A flaw was found in Open vSwitch where multiple versions are vulnerable to crafted Geneve packets, which may result in a denial of service and invalid memory accesses. Triggering this issue requires that hardware offloading via the netlink path is enabled.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LFZADABUDOFI2KZIRQBYFZCIKH55RGY3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VYYUBF6OW2JG7VOFEOROHXGSJCTES3QO/
- https://packages.fedoraproject.org/
- https://repos.fedorapeople.org/repos/openstack/
- https://access.redhat.com/security/cve/CVE-2023-3966
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3966.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3966
- https://bugzilla.redhat.com/show_bug.cgi?id=2178363
