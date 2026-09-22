# [H] rapidio: fix an API misues when rio_add_net() fails

## Summary
Severity: High
Advisory: CVE-2025-21934
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21934
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

rapidio: fix an API misues when rio_add_net() fails

rio_add_net() calls device_register() and fails when device_register()
fails.  Thus, put_device() should be used rather than kfree().  Add
"mport->net = NULL;" to avoid a use after free issue.

## References
- https://git.kernel.org/stable/c/22e4977141dfc6d109bf29b495bf2187b4250990
- https://git.kernel.org/stable/c/2537f01d57f08c527e40bbb5862aa6ff43344898
- https://git.kernel.org/stable/c/88ddad53e4cfb6de861c6d4fb7b25427f46baed5
- https://git.kernel.org/stable/c/a5f5e520e8fbc6294020ff8afa36f684d92c6e6a
- https://git.kernel.org/stable/c/b2ef51c74b0171fde7eb69b6152d3d2f743ef269
- https://git.kernel.org/stable/c/cdd9f58f7fe41a55fae4305ea51fc234769fd466
- https://git.kernel.org/stable/c/d4ec862ce80f64db923a1d942b5d11cf6fc87d36
- https://git.kernel.org/stable/c/f0aa4ee1cbbf7789907e5a3f6810de01c146c211
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21934.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21934
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
