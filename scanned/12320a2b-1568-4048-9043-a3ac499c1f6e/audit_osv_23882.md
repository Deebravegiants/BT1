# [M] pinctrl: aspeed: Fix potential NULL dereference in aspeed_pinmux_set_mux()

## Summary
Severity: Medium
Advisory: CVE-2022-49618
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49618
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: aspeed: Fix potential NULL dereference in aspeed_pinmux_set_mux()

pdesc could be null but still dereference pdesc->name and it will lead to
a null pointer access. So we move a null check before dereference.

## References
- https://git.kernel.org/stable/c/3cb392b64304a05bf647e2e44efacd9a1f3c3c6a
- https://git.kernel.org/stable/c/84a85d3fef2e75b1fe9fc2af6f5267122555a1ed
- https://git.kernel.org/stable/c/e162a24f1dd06c0dcae71f2565c9f3da2827b98e
- https://git.kernel.org/stable/c/ef1e38532f4b2f0f3b460e938a2e7076c3bed5ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49618.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49618
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
