# [H] x86/sev: Use TSC_FACTOR for Secure TSC frequency calculation

## Summary
Severity: High
Advisory: CVE-2025-38508
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38508
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/sev: Use TSC_FACTOR for Secure TSC frequency calculation

When using Secure TSC, the GUEST_TSC_FREQ MSR reports a frequency based on
the nominal P0 frequency, which deviates slightly (typically ~0.2%) from
the actual mean TSC frequency due to clocking parameters.

Over extended VM uptime, this discrepancy accumulates, causing clock skew
between the hypervisor and a SEV-SNP VM, leading to early timer interrupts as
perceived by the guest.

The guest kernel relies on the reported nominal frequency for TSC-based
timekeeping, while the actual frequency set during SNP_LAUNCH_START may
differ. This mismatch results in inaccurate time calculations, causing the
guest to perceive hrtimers as firing earlier than expected.

Utilize the TSC_FACTOR from the SEV firmware's secrets page (see "Secrets
Page Format" in the SNP Firmware ABI Specification) to calculate the mean
TSC frequency, ensuring accurate timekeeping and mitigating clock skew in
SEV-SNP VMs.

Use early_ioremap_encrypted() to map the secrets page as
ioremap_encrypted() uses kmalloc() which is not available during early TSC
initialization and causes a panic.

  [ bp: Drop the silly dummy var:
    https://lore.kernel.org/r/20250630192726.GBaGLlHl84xIopx4Pt@fat_crate.local ]

## References
- https://git.kernel.org/stable/c/52e1a03e6cf61ae165f59f41c44394a653a0a788
- https://git.kernel.org/stable/c/d0195c42e65805938c9eb507657e7cdf8e1e9522
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38508.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
