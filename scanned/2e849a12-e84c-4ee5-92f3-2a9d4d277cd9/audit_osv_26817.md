# [H] mptcp: fix NULL pointer dereference on fastopen early fallback

## Summary
Severity: High
Advisory: CVE-2023-54085
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54085
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix NULL pointer dereference on fastopen early fallback

In case of early fallback to TCP, subflow_syn_recv_sock() deletes
the subflow context before returning the newly allocated sock to
the caller.

The fastopen path does not cope with the above unconditionally
dereferencing the subflow context.

## References
- https://git.kernel.org/stable/c/95135835519b0ab931c39908b2c99e9fb3c9068b
- https://git.kernel.org/stable/c/c0ff6f6da66a7791a32c0234388b1bdc00244917
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54085.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
