# [H] bpf: Fix out-of-bounds dynptr write in bpf_crypto_crypt

## Summary
Severity: High
Advisory: CVE-2025-39917
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39917
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix out-of-bounds dynptr write in bpf_crypto_crypt

Stanislav reported that in bpf_crypto_crypt() the destination dynptr's
size is not validated to be at least as large as the source dynptr's
size before calling into the crypto backend with 'len = src_len'. This
can result in an OOB write when the destination is smaller than the
source.

Concretely, in mentioned function, psrc and pdst are both linear
buffers fetched from each dynptr:

  psrc = __bpf_dynptr_data(src, src_len);
  [...]
  pdst = __bpf_dynptr_data_rw(dst, dst_len);
  [...]
  err = decrypt ?
        ctx->type->decrypt(ctx->tfm, psrc, pdst, src_len, piv) :
        ctx->type->encrypt(ctx->tfm, psrc, pdst, src_len, piv);

The crypto backend expects pdst to be large enough with a src_len length
that can be written. Add an additional src_len > dst_len check and bail
out if it's the case. Note that these kfuncs are accessible under root
privileges only.

## References
- https://git.kernel.org/stable/c/0126358df12d6f476f79251d9c398ac5c1b3062d
- https://git.kernel.org/stable/c/c4be24ef0510c146dca4671effb127e97631534b
- https://git.kernel.org/stable/c/f9bb6ffa7f5ad0f8ee0f53fc4a10655872ee4a14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39917.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39917
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
