# [H] nvmet-tcp: Fix a kernel panic when host sends an invalid H2C PDU length

## Summary
Severity: High
Advisory: CVE-2023-52454
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2023-52454
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: Fix a kernel panic when host sends an invalid H2C PDU length

If the host sends an H2CData command with an invalid DATAL,
the kernel may crash in nvmet_tcp_build_pdu_iovec().

Unable to handle kernel NULL pointer dereference at
virtual address 0000000000000000
lr : nvmet_tcp_io_work+0x6ac/0x718 [nvmet_tcp]
Call trace:
  process_one_work+0x174/0x3c8
  worker_thread+0x2d0/0x3e8
  kthread+0x104/0x110

Fix the bug by raising a fatal error if DATAL isn't coherent
with the packet size.
Also, the PDU length should never exceed the MAXH2CDATA parameter which
has been communicated to the host in nvmet_tcp_handle_icreq().

## References
- https://git.kernel.org/stable/c/24e05760186dc070d3db190ca61efdbce23afc88
- https://git.kernel.org/stable/c/2871aa407007f6f531fae181ad252486e022df42
- https://git.kernel.org/stable/c/4cb3cf7177ae3666be7fb27d4ad4d72a295fb02d
- https://git.kernel.org/stable/c/70154e8d015c9b4fb56c1a2ef1fc8b83d45c7f68
- https://git.kernel.org/stable/c/ee5e7632e981673f42a50ade25e71e612e543d9d
- https://git.kernel.org/stable/c/efa56305908ba20de2104f1b8508c6a7401833be
- https://git.kernel.org/stable/c/f775f2621c2ac5cc3a0b3a64665dad4fb146e510
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52454.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
