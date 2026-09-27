# [H] rxrpc: Fix error handling in rxgk_extract_token()

## Summary
Severity: High
Advisory: CVE-2026-46010
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46010
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix error handling in rxgk_extract_token()

Fix a missing bit of error handling in rxgk_extract_token(): in the event
that rxgk_decrypt_skb() returns -ENOMEM, it should just return that rather
than continuing on (for anything else, it generates an abort).

## References
- https://git.kernel.org/stable/c/293095ef618818852bac5488c1bc223935e2ca17
- https://git.kernel.org/stable/c/3476c8bb960f48e49355d6f93fb7673211e0163f
- https://git.kernel.org/stable/c/c52803e925604e2a17962ab0c99dce2d3f7238db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46010.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46010
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
