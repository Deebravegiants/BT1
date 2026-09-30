# [H] thunderbolt: Clamp XDomain response data copy to allocation size

## Summary
Severity: High
Advisory: CVE-2026-53148
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53148
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Clamp XDomain response data copy to allocation size

tb_xdp_properties_request() derives the per-packet copy length from
the response header without checking that it fits in the previously
allocated data buffer.  A malicious peer can set its length field
larger than the declared data_length, causing memcpy to write past
the kcalloc allocation.

Clamp the per-packet copy length so that the cumulative offset
never exceeds data_len.

## References
- https://git.kernel.org/stable/c/05a43157676c243c248d1c6d9dcecbe6eba2f35d
- https://git.kernel.org/stable/c/0b334279a82d79fb4723bd4f614305de1ab69caa
- https://git.kernel.org/stable/c/322e93448d908434ae5545660fcbe8f5a7a8e141
- https://git.kernel.org/stable/c/5db10c8ad8c09f72c847dfeef3d876098257f505
- https://git.kernel.org/stable/c/6021d39ccd979713b39b980286020d8f9a45efd1
- https://git.kernel.org/stable/c/89ae04365e01d5ae4aae83044a8bbd2a9aaf8d0d
- https://git.kernel.org/stable/c/906035d5c3784570191d259cbf9a0ac1617852b5
- https://git.kernel.org/stable/c/fcbd0cdab92838854a5818be7ed8a097164ef6d5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53148.json
- https://access.redhat.com/security/cve/CVE-2026-53148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53148
- https://bugzilla.redhat.com/show_bug.cgi?id=2492756
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
