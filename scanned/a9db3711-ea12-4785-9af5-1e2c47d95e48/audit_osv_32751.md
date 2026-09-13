# [M] sfc: fix NULL dereferences in ef100_process_design_param()

## Summary
Severity: Medium
Advisory: CVE-2025-37860
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-37860
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.57, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: fix NULL dereferences in ef100_process_design_param()

Since cited commit, ef100_probe_main() and hence also
 ef100_check_design_params() run before efx->net_dev is created;
 consequently, we cannot netif_set_tso_max_size() or _segs() at this
 point.
Move those netif calls to ef100_probe_netdev(), and also replace
 netif_err within the design params code with pci_err.

## References
- https://git.kernel.org/stable/c/8241ecec1cdc6699ae197d52d58e76bddd995fa5
- https://git.kernel.org/stable/c/e56391011381d6d029da377a65ac314cb3d5def2
- https://git.kernel.org/stable/c/f21623b8446735b5e2ac5f8ee69b8743177d7b19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37860.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
