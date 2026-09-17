# [C] rxrpc: Fix integer overflow in rxgk_verify_response()

## Summary
Severity: Critical
Advisory: CVE-2026-31633
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31633
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix integer overflow in rxgk_verify_response()

In rxgk_verify_response(), there's a potential integer overflow due to
rounding up token_len before checking it, thereby allowing the length check to
be bypassed.

Fix this by checking the unrounded value against len too (len is limited as
the response must fit in a single UDP packet).

## References
- https://git.kernel.org/stable/c/1f864d9daaf622aeaa774404fd51e7d6a435b046
- https://git.kernel.org/stable/c/699e52180f4231c257821c037ed5c99d5eb0edb8
- https://git.kernel.org/stable/c/c1e242beb6b1efc3c286f617e8d940c8fbf2ed41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31633.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31633
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
