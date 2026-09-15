# [H] NFSD: Fix crash in nfsd4_read_release()

## Summary
Severity: High
Advisory: CVE-2025-40324
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40324
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.3.0 <6.12.58, >=6.7.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix crash in nfsd4_read_release()

When tracing is enabled, the trace_nfsd_read_done trace point
crashes during the pynfs read.testNoFh test.

## References
- https://git.kernel.org/stable/c/03524ccff698d4a77d096ed529073d91f5edee5d
- https://git.kernel.org/stable/c/2ac46606b2cc49e78d8e3d8f2685e79e9ba73020
- https://git.kernel.org/stable/c/375fdd8993cecc48afa359728a6e70b280dde1c8
- https://git.kernel.org/stable/c/8f244b773c63fa480c9a3bd1ae04f5272f285e89
- https://git.kernel.org/stable/c/930cb4fe3ab4061be31f20ee30bb72a66f7bb6d1
- https://git.kernel.org/stable/c/a4948875ed0599c037dc438c11891c9012721b1d
- https://git.kernel.org/stable/c/abb1f08a2121dd270193746e43b2a9373db9ad84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40324.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
