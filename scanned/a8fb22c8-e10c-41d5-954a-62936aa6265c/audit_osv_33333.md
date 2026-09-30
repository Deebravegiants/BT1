# [H] sunrpc: fix null pointer dereference on zero-length checksum

## Summary
Severity: High
Advisory: CVE-2025-40129
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40129
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: fix null pointer dereference on zero-length checksum

In xdr_stream_decode_opaque_auth(), zero-length checksum.len causes
checksum.data to be set to NULL. This triggers a NPD when accessing
checksum.data in gss_krb5_verify_mic_v2(). This patch ensures that
the value of checksum.len is not less than XDR_UNIT.

## References
- https://git.kernel.org/stable/c/6df164e29bd4e6505c5a2e0e5f1e1f6957a16a42
- https://git.kernel.org/stable/c/81cec07d303186d0d8c623ef8b5ecd3b81e94cf6
- https://git.kernel.org/stable/c/ab9a70cd2386a0d70c164b0905dd66bc9af52e77
- https://git.kernel.org/stable/c/affc03d44921f493deaae1d33151e3067a6f9f8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40129.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
