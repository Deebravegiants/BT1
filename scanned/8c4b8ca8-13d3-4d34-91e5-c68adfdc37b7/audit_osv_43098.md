# [H] apparmor: aa_label_alloc use aa_label_free on alloc failure

## Summary
Severity: High
Advisory: CVE-2026-72459
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72459
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: aa_label_alloc use aa_label_free on alloc failure

aa_label_alloc() allocates a secid before allocating or taking the label
proxy. If the later proxy step fails, the error path only freed the label
memory, leaking any resources initialized by aa_label_init().

Use aa_label_free() on the failure path so partially initialized labels
release their secid and other label resources before the backing memory is
freed.

## References
- https://git.kernel.org/stable/c/654fe7505dc6889724d4094fa64f89991afabfc3
- https://git.kernel.org/stable/c/6d91479174240f39e9edea250d95fa08c678a207
- https://git.kernel.org/stable/c/7cb69e109610bba500e1ecb870f7988a4717208a
- https://git.kernel.org/stable/c/ae02e603c0b39b29f3ce6fe3efe01b286af1a2a4
- https://git.kernel.org/stable/c/b14fbacad77d64594228983ec20d61a224f3f491
- https://git.kernel.org/stable/c/b5a9da5d36162d34db0f36abb15420e295176793
- https://git.kernel.org/stable/c/bf310b044e85d4de670c94295c5d8e4c5bc5e7bc
- https://git.kernel.org/stable/c/cc2192899d502e3321e60cf1e91421e7309d089c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
