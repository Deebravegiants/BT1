# [H] x86/microcode/AMD: Fix __apply_microcode_amd()'s return value

## Summary
Severity: High
Advisory: CVE-2025-22047
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22047
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/microcode/AMD: Fix __apply_microcode_amd()'s return value

When verify_sha256_digest() fails, __apply_microcode_amd() should propagate
the failure by returning false (and not -1 which is promoted to true).

## References
- https://git.kernel.org/stable/c/31ab12df723543047c3fc19cb8f8c4498ec6267f
- https://git.kernel.org/stable/c/763f4d638f71cb45235395790a46e9f9e84227fd
- https://git.kernel.org/stable/c/7f705a45f130a85fbf31c2abdc999c65644c8307
- https://git.kernel.org/stable/c/ada88219d5315fc13f2910fe278c7112d8d68889
- https://git.kernel.org/stable/c/d295c58fad1d5ab987a81f139dd21498732c4f13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22047.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
