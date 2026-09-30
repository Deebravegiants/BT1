# [M] Libvirt: null pointer dereference in udevconnectlistallinterfaces()

## Summary
Severity: Medium
Advisory: CVE-2024-2496
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-2496
Type: osv

## Details
A NULL pointer dereference flaw was found in the udevConnectListAllInterfaces() function in libvirt. This issue can occur when detaching a host interface while at the same time collecting the list of interfaces via virConnectListAllInterfaces API. This flaw could be used to perform a denial of service attack by causing the libvirt daemon to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://access.redhat.com/errata/RHSA-2024:2236
- https://access.redhat.com/security/cve/CVE-2024-2496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2496.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2496
- https://bugzilla.redhat.com/show_bug.cgi?id=2269672
- https://gitlab.com/libvirt/libvirt/
