# [H] vp_vdpa: fix id_table array not null terminated error

## Summary
Severity: High
Advisory: CVE-2024-53110
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53110
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vp_vdpa: fix id_table array not null terminated error

Allocate one extra virtio_device_id as null terminator, otherwise
vdpa_mgmtdev_get_classes() may iterate multiple times and visit
undefined memory.

## References
- https://git.kernel.org/stable/c/0a886489d274596ad1a80789d3a773503210a615
- https://git.kernel.org/stable/c/4e39ecadf1d2a08187139619f1f314b64ba7d947
- https://git.kernel.org/stable/c/870d68fe17b5d9032049dcad98b5781a344a8657
- https://git.kernel.org/stable/c/c4d64534d4b1c47d2f1ce427497f971ad4735aae
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53110.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
