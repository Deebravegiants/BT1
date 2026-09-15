# [C] RDMA/srp: bound SRP_RSP sense copy by the received length

## Summary
Severity: Critical
Advisory: CVE-2026-53186
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53186
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/srp: bound SRP_RSP sense copy by the received length

srp_process_rsp() copies sense data from rsp->data + resp_data_len,
where resp_data_len is the full 32-bit value supplied by the SRP target
and is never checked against the number of bytes actually received
(wc->byte_len). The copy length is bounded to SCSI_SENSE_BUFFERSIZE, so
at most 96 bytes are copied, but the source offset is not bounded.

A malicious or compromised SRP target on the InfiniBand/RoCE fabric that
the initiator has logged into can return an SRP_RSP with
SRP_RSP_FLAG_SNSVALID set and a large resp_data_len. The receive buffer
is allocated at the target-chosen max_ti_iu_len, so the source of the
sense copy lands past the bytes actually received; with resp_data_len
near 0xFFFFFFFF it is gigabytes past the buffer and the read faults.

Copy the sense data only if it has not been truncated, that is, only if
the response header, the response data, and the sense region fit within
the bytes actually received; otherwise drop the sense and log. The
in-tree iSER and NVMe-RDMA receive paths already bound their parse by
wc->byte_len; this brings ib_srp into line with them.

## References
- https://git.kernel.org/stable/c/0b9ee09d5e849591f17d98c078033dadea967293
- https://git.kernel.org/stable/c/0d64bc200ebe4f275b27438c6e593903e0b16fe1
- https://git.kernel.org/stable/c/13e91fd076306f5d0cdfa14f53d69e37274723c4
- https://git.kernel.org/stable/c/2015038195939eac54a1ee83c9d98ef1a8ccbbce
- https://git.kernel.org/stable/c/3523e53ff95f1837ec3f57ff7558532bcb2661b7
- https://git.kernel.org/stable/c/3889517c2ec7f364914aea8209abfff735f7ecde
- https://git.kernel.org/stable/c/ed77cc819ad631264787cade5ae5ec4c535ec6bb
- https://git.kernel.org/stable/c/f92a285db7ff6e598591ccbfb551be155c5f4d57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53186.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
