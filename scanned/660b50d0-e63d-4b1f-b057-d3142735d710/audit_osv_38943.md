# [H] KVM: nSVM: Always use vmcb01 in VMLOAD/VMSAVE emulation

## Summary
Severity: High
Advisory: CVE-2026-43133
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43133
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nSVM: Always use vmcb01 in VMLOAD/VMSAVE emulation

Commit cc3ed80ae69f ("KVM: nSVM: always use vmcb01 to for vmsave/vmload
of guest state") made KVM always use vmcb01 for the fields controlled by
VMSAVE/VMLOAD, but it missed updating the VMLOAD/VMSAVE emulation code
to always use vmcb01.

As a result, if VMSAVE/VMLOAD is executed by an L2 guest and is not
intercepted by L1, KVM will mistakenly use vmcb02. Always use vmcb01
instead of the current VMCB.

## References
- https://git.kernel.org/stable/c/0004ecb798b30e90d7ebfe74efae2d9423315a64
- https://git.kernel.org/stable/c/10063e1251c1485034a018236080792ad083dcc5
- https://git.kernel.org/stable/c/127ccae2c185f62e6ecb4bf24f9cb307e9b9c619
- https://git.kernel.org/stable/c/3880e331b0b31d0d5d3702b124f6c93539cd478a
- https://git.kernel.org/stable/c/c3b7015000988ba35ecd5648f4b2283960f00543
- https://git.kernel.org/stable/c/d464cf1ed900d47c85393d40b00017b6adfc2e6c
- https://git.kernel.org/stable/c/fce2fd4a2ca05670a91015aacccf96a1c26268fd
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43133.json
- https://access.redhat.com/errata/RHSA-2026:65334
- https://access.redhat.com/errata/RHSA-2026:66180
- https://access.redhat.com/security/cve/CVE-2026-43133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43133.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43133
- https://bugzilla.redhat.com/show_bug.cgi?id=2467065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
