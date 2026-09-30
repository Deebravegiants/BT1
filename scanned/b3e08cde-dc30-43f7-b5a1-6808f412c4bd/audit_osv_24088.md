# [H] NFSv4/pnfs: Fix a use-after-free bug in open

## Summary
Severity: High
Advisory: CVE-2022-50072
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50072
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.138, >=5.11.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4/pnfs: Fix a use-after-free bug in open

If someone cancels the open RPC call, then we must not try to free
either the open slot or the layoutget operation arguments, since they
are likely still in use by the hung RPC call.

## References
- https://git.kernel.org/stable/c/0fffb46ff3d5ed4668aca96441ec7a25b793bd6f
- https://git.kernel.org/stable/c/2135e5d56278ffdb1c2e6d325dc6b87f669b9dac
- https://git.kernel.org/stable/c/76ffd2042438769298f34b76102b40dea89de616
- https://git.kernel.org/stable/c/a4cf3dadd1fa43609f7c6570c9116b0e0a9923d1
- https://git.kernel.org/stable/c/b03d1117e9be7c7da60e466eaf9beed85c5916c8
- https://git.kernel.org/stable/c/f7ee3b772d9de87387a725caa04bc041ac7fe5ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50072.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
