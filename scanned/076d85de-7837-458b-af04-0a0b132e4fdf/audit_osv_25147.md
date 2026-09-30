# [M] Service monitor mac flow is not rate limited

## Summary
Severity: Medium
Advisory: CVE-2023-3153
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-3153
Type: osv

## Details
A flaw was found in Open Virtual Network where the service monitor MAC does not properly rate limit. This issue could allow an attacker to cause a denial of service, including on deployments with CoPP enabled and properly configured.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://mail.openvswitch.org/pipermail/ovs-announce/2023-August/000327.html
- https://mail.openvswitch.org/pipermail/ovs-dev/2023-August/407553.html
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-3153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3153.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3153
- https://bugzilla.redhat.com/show_bug.cgi?id=2213279
- https://github.com/ovn-org/ovn/issues/198
- https://github.com/ovn-org/ovn/commit/9a3f7ed905e525ebdcb14541e775211cbb0203bd
