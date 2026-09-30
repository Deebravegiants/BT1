# [M] CVE-2023-2700

## Summary
Severity: Medium
Advisory: CVE-2023-2700
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-2700
Type: osv

## Details
A vulnerability was found in libvirt. This security flaw ouccers due to repeatedly querying an SR-IOV PCI device's capabilities that exposes a memory leak caused by a failure to free the virPCIVirtualFunction array within the parent struct's g_autoptr cleanup.

## References
- https://access.redhat.com/security/cve/CVE-2023-2700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2700.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EVK6JKP36CHE7YAFDJNPNLTW4OWJJ7TQ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-2700
- https://security.netapp.com/advisory/ntap-20230706-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2203653
- https://gitlab.com/libvirt/libvirt/-/commit/6425a311b8ad19d6f9c0b315bf1d722551ea3585#874a1e768ade6ceb4538931cbc06248e73223306
