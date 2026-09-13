# [H] KVM: arm64: Disassociate vcpus from redistributor region on teardown

## Summary
Severity: High
Advisory: CVE-2024-40989
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40989
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Disassociate vcpus from redistributor region on teardown

When tearing down a redistributor region, make sure we don't have
any dangling pointer to that region stored in a vcpu.

## References
- https://git.kernel.org/stable/c/0d92e4a7ffd5c42b9fa864692f82476c0bf8bcc8
- https://git.kernel.org/stable/c/152b4123f21e6aff31cea01158176ad96a999c76
- https://git.kernel.org/stable/c/48bb62859d47c5c4197a8c01128d0fa4f46ee58c
- https://git.kernel.org/stable/c/68df4fc449fcc24347209e500ce26d5816705a77
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40989.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40989
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
