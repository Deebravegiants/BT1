# [H] KVM: nSVM: Raise #UD if unhandled VMMCALL isn't intercepted by L1

## Summary
Severity: High
Advisory: CVE-2026-46076
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46076
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nSVM: Raise #UD if unhandled VMMCALL isn't intercepted by L1

Explicitly synthesize a #UD for VMMCALL if L2 is active, L1 does NOT want
to intercept VMMCALL, nested_svm_l2_tlb_flush_enabled() is true, and the
hypercall is something other than one of the supported Hyper-V hypercalls.
When all of the above conditions are met, KVM will intercept VMMCALL but
never forward it to L1, i.e. will let L2 make hypercalls as if it were L1.

The TLFS says a whole lot of nothing about this scenario, so go with the
architectural behavior, which says that VMMCALL #UDs if it's not
intercepted.

Opportunistically do a 2-for-1 stub trade by stub-ifying the new API
instead of the helpers it uses.  The last remaining "single" stub will
soon be dropped as well.

[sean: rewrite changelog and comment, tag for stable, remove defunct stubs]

## References
- https://git.kernel.org/stable/c/009c0f726abeaa67aad1d96b883bdce01d405ce2
- https://git.kernel.org/stable/c/5fb4a5f361565f5b629d8a8fe5288ce8463c5727
- https://git.kernel.org/stable/c/924d721fae95687acedbaf624a094ed0e8b67104
- https://git.kernel.org/stable/c/c36991c6f8d2ab56ee67aff04e3c357f45cfc76c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
