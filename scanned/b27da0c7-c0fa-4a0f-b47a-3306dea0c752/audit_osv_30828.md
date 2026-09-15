# [H] af_packet: avoid erroring out after sock_init_data() in packet_create()

## Summary
Severity: High
Advisory: CVE-2024-56606
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56606
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_packet: avoid erroring out after sock_init_data() in packet_create()

After sock_init_data() the allocated sk object is attached to the provided
sock object. On error, packet_create() frees the sk object leaving the
dangling pointer in the sock object on return. Some other code may try
to use this pointer and cause use-after-free.

## References
- https://git.kernel.org/stable/c/132e615bb1d7cdec2d3cfbdec2efa630e923fd21
- https://git.kernel.org/stable/c/157f08db94123e2ba56877dd0ac88908b13a5dd0
- https://git.kernel.org/stable/c/1dc1e1db927056cb323296e2294a855cd003dfe7
- https://git.kernel.org/stable/c/46f2a11cb82b657fd15bab1c47821b635e03838b
- https://git.kernel.org/stable/c/71b22837a5e55ac27d6a14b9cdf2326587405c4f
- https://git.kernel.org/stable/c/a6cf750b737374454a4e03a5ed449a3eb0c96414
- https://git.kernel.org/stable/c/fd09880b16d33aa5a7420578e01cd79148fa9829
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56606.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
