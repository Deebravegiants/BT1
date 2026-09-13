# [M] ASoC: imx-audmix: Add NULL check in imx_audmix_probe

## Summary
Severity: Medium
Advisory: CVE-2024-53199
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53199
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: imx-audmix: Add NULL check in imx_audmix_probe

devm_kasprintf() can return a NULL pointer on failure,but this
returned value in imx_audmix_probe() is not checked.
Add NULL check in imx_audmix_probe(), to handle kernel NULL
pointer dereference error.

## References
- https://git.kernel.org/stable/c/c040cbe2e13da6454ae4748e04e53d885e1c9603
- https://git.kernel.org/stable/c/dc5aa71f39b44d8117b2417dafd0e2884a75dd37
- https://git.kernel.org/stable/c/e038f43edaf0083f6aa7c9415d86cf28dfd152f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53199.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
