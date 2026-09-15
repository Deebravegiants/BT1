# [H] ASoC: SOF: ipc4-control: Fix TOCTOU in sof_ipc4_bytes_put

## Summary
Severity: High
Advisory: CVE-2026-72304
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72304
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc4-control: Fix TOCTOU in sof_ipc4_bytes_put

In sof_ipc4_bytes_put(), the copy size is derived from the old
data->size in the buffer rather than the incoming new data's size
field from ucontrol. If the new data has a different size, the copy
uses the wrong length: it may truncate valid data or copy stale bytes.

Fix by validating and using the incoming data's sof_abi_hdr.size from
ucontrol before copying.

## References
- https://git.kernel.org/stable/c/038406abde0d0883419ec89425ea941ec8bbef95
- https://git.kernel.org/stable/c/266f936db83aee6ca6473bbb06259bda52bf4fc3
- https://git.kernel.org/stable/c/3ad673e7139cf214afd24321a829aad6575f4163
- https://git.kernel.org/stable/c/4cf6a7ebbf8787393b158b2cc341723e5bebc4a8
- https://git.kernel.org/stable/c/fb4293173db2d474d8fbc0e5ecf4943e6df2b40e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72304.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
