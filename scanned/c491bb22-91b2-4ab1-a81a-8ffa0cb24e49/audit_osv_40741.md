# [M] Prefix-substitution forgery via integer overflow in wolfCrypt CMAC

## Summary
Severity: Medium
Advisory: CVE-2026-5477
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5477
Type: osv

## Details
An integer overflow existed in the wolfCrypt CMAC implementation, that could be exploited to forge CMAC tags. The function wc_CmacUpdate used the guard `if (cmac->totalSz != 0)` to skip XOR-chaining on the first block (where digest is all-zeros and the XOR is a no-op). However, totalSz is word32 and wraps to zero after 2^28 block flushes (4 GiB), causing the guard to erroneously discard the live CBC-MAC chain state. Any two messages sharing a common suffix beyond the 4 GiB mark then produce identical CMAC tags, enabling a zero-work prefix-substitution forgery. The fix removes the guard, making the XOR unconditional; the no-op property on the first block is preserved because digest is zero-initialized by wc_InitCmac_ex.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5477.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5477
- https://github.com/wolfSSL/wolfssl/pull/10102
