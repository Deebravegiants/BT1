# [H] KVM: SEV: Use READ_ONCE() when reading entries/indices from PSC buffer

## Summary
Severity: High
Advisory: CVE-2026-63937
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63937
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SEV: Use READ_ONCE() when reading entries/indices from PSC buffer

Use READ_ONCE() when reading entries/indices from the guest-accessible
Page State Change buffer to defend against TOCTOU bugs.

Don't bother with READ_ONCE()/WRITE_ONCE() for cases where KVM is writing
(and not consuming the result!), as the guest isn't supposed to touch the
buffer while it's being processed.  I.e. using READ_ONCE() is all about
protecting against misbehaving guests.

## References
- https://git.kernel.org/stable/c/b1dfaa6f7a957726a6800135be3659fbe4bbf2a4
- https://git.kernel.org/stable/c/bd232801ef1d1fd985d2d4ca3cd1d888303ca86f
- https://git.kernel.org/stable/c/c8cc238093ca6c99267032f6cfe78f59389f3157
- https://git.kernel.org/stable/c/edbbe88f83b524434974e84808d3093199d67c24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63937.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63937
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
