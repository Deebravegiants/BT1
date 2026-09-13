# [M] Libvirt: negative g_new0 length can lead to unbounded memory allocation

## Summary
Severity: Medium
Advisory: CVE-2024-2494
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-2494
Type: osv

## Details
A flaw was found in the RPC library APIs of libvirt. The RPC server deserialization code allocates memory for arrays before the non-negative length check is performed by the C API entry points. Passing a negative length to the g_new0 function results in a crash due to the negative length being treated as a huge positive number. This flaw allows a local, unprivileged user to perform a denial of service attack by causing the libvirt daemon to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://lists.libvirt.org/archives/list/devel@lists.libvirt.org/thread/BKRQXPLPC6B7FLHJXSBQYW7HNDEBW6RJ/
- https://access.redhat.com/errata/RHSA-2024:2560
- https://access.redhat.com/errata/RHSA-2024:3253
- https://access.redhat.com/security/cve/CVE-2024-2494
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2494.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2494
- https://security.netapp.com/advisory/ntap-20240517-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=2270115
- https://gitlab.com/libvirt/libvirt/
