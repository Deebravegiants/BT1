# [M] crypto: qat - fix memory leak in RSA

## Summary
Severity: Medium
Advisory: CVE-2022-49566
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49566
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - fix memory leak in RSA

When an RSA key represented in form 2 (as defined in PKCS #1 V2.1) is
used, some components of the private key persist even after the TFM is
released.
Replace the explicit calls to free the buffers in qat_rsa_exit_tfm()
with a call to qat_rsa_clear_ctx() which frees all buffers referenced in
the TFM context.

## References
- https://git.kernel.org/stable/c/0f967fdc09955221a1951a279481b0bf4d359941
- https://git.kernel.org/stable/c/80a52e1ee7757b742f96bfb0d58f0c14eb6583d0
- https://git.kernel.org/stable/c/a843925e0287eebb4aa808666bf22c664dfe4c53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49566.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
