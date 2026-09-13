# [H] ASoC: SOF: ipc3-control: Fix TOCTOU in bytes_put and bytes_get

## Summary
Severity: High
Advisory: CVE-2026-72301
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72301
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc3-control: Fix TOCTOU in bytes_put and bytes_get

In sof_ipc3_bytes_put(), the size used for the memcpy is derived from
the old data->size already in the buffer, not the incoming new data's
size field. If the new data has a different size, the copy length is
wrong: it may truncate valid data or copy stale bytes.

Similarly, sof_ipc3_bytes_get() checks data->size against max_size
without accounting for the sizeof(struct sof_ipc_ctrl_data) offset
of the flex array within the allocation.

Fix bytes_put to validate and use the incoming data's sof_abi_hdr.size
from ucontrol before copying. Fix bytes_get to subtract sizeof(*cdata)
from the bounds check to match the actual available space.

## References
- https://git.kernel.org/stable/c/0c4fbdaca225b97122b61b68c5353caa33a253c3
- https://git.kernel.org/stable/c/0dce240145f47545d2e4b18c6d58033b83e1fd0e
- https://git.kernel.org/stable/c/1f97760417b5faa60e9642fd0ed61eb17d0b1b39
- https://git.kernel.org/stable/c/8bd715a9d882fe1993bb2aec5eff89fffa946592
- https://git.kernel.org/stable/c/92f90917413bdd6078fefff6f6c83a07bf870b04
- https://git.kernel.org/stable/c/ed4f758f34be4c32e02933ac4fa044589d9c1c16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72301.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72301
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
