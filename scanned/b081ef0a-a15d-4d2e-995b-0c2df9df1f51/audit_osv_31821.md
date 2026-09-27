# [H] io_uring/kbuf: reallocate buf lists on upgrade

## Summary
Severity: High
Advisory: CVE-2025-21836
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-07
Source: https://osv.dev/vulnerability/CVE-2025-21836
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/kbuf: reallocate buf lists on upgrade

IORING_REGISTER_PBUF_RING can reuse an old struct io_buffer_list if it
was created for legacy selected buffer and has been emptied. It violates
the requirement that most of the field should stay stable after publish.
Always reallocate it instead.

## References
- https://git.kernel.org/stable/c/146a185f6c05ee263db715f860620606303c4633
- https://git.kernel.org/stable/c/2a5febbef40ce968e295a7aeaa5d5cbd9e3e5ad4
- https://git.kernel.org/stable/c/7d0dc28dae836caf7645fef62a10befc624dd17b
- https://git.kernel.org/stable/c/8802766324e1f5d414a81ac43365c20142e85603
- https://u1f383.github.io/slides/talks/2025_Hexacon-Deja_Vu_in_Linux_io_uring_Breaking_Memory_Sharing_Again_After_Generations_of_Fixes.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21836.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21836
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
