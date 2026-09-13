# [H] crypto: tegra - fix rctx->cryptlen calculation in tegra_gcm_do_one_req()

## Summary
Severity: High
Advisory: CVE-2026-80522
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80522
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: tegra - fix rctx->cryptlen calculation in tegra_gcm_do_one_req()

Perform rctx->cryptlen calculation in tegra_gcm_do_one_req() the same way
it is done in tegra_ccm_crypt_init(). The current formulae may lead to a
crash if a caller does not call tegra_gcm_setauthsize() and so ctx->authsize
remains zero. Then a decrypt operation with incorrect rctx->cryptlen will
lead to a write beyound rctx->dst_sg buffer.

As a follow-up cleanup delete struct tegra_aead_ctx->authsize field since
it appears to be completely unused. Also simplify tegra_ccm_setauthsize()
and tegra_gcm_setauthsize() functions respectively.

## References
- https://git.kernel.org/stable/c/360f2974fcea49c61f6d6f81554741a9eeee7168
- https://git.kernel.org/stable/c/99a18e1d979e0fad3aaf9c65ae6696897c1d9869
- https://git.kernel.org/stable/c/c6237834d9994de209cb90c7a2c461247bce8e90
- https://git.kernel.org/stable/c/cd6991001bf0681ed0bcf21f9cc3d261d749b2bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80522
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
