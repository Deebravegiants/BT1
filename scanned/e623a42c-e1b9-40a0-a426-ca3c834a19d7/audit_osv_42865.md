# [H] octeontx2-af: cn10k: restrict VF LMTLINE sharing to its own PF

## Summary
Severity: High
Advisory: CVE-2026-72045
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72045
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: cn10k: restrict VF LMTLINE sharing to its own PF

rvu_mbox_handler_lmtst_tbl_setup() uses req->base_pcifunc as a direct
index into the LMT map table to read another function's LMTLINE
physical base address and copy it into the caller's own LMT map table
entry. The mailbox dispatcher authenticates req->hdr.pcifunc from the
IRQ source, but req->base_pcifunc is a separate payload field and is
not sanitized.

Reject the request with -EPERM when a VF caller's base_pcifunc is not a
valid function under its own PF. is_pf_func_valid() bounds the FUNC field
to the PF's configured VF count, keeping the computed index inside the
caller's own slot block.

## References
- https://git.kernel.org/stable/c/04c014e49b9f53d58a8f94adece8a0af3ae1b85c
- https://git.kernel.org/stable/c/54535692bec9ef464adc714108eb19e49e38b5a2
- https://git.kernel.org/stable/c/59da37fee81a8d76079313348ca13c5bc90dd6ae
- https://git.kernel.org/stable/c/6967dd944be2a71eddab3a2ae1a1a4dd9e5f8eed
- https://git.kernel.org/stable/c/8cdcf3d2caacdee7ddd363705fb4d93b0c1a0915
- https://git.kernel.org/stable/c/c73b8795b45f4ad5a95120d2e9b435ea4616e08e
- https://git.kernel.org/stable/c/e9c5b03208507dd6d58b0c23a2c60b5c2f4c1b11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72045.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
