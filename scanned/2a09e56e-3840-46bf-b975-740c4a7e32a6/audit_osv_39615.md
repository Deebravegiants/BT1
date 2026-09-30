# [H] net: skbuff: preserve shared-frag marker during coalescing

## Summary
Severity: High
Advisory: CVE-2026-46300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-23
Source: https://osv.dev/vulnerability/CVE-2026-46300
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.257, >=5.11.0 <5.15.208, >=5.16.0 <6.1.174, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: skbuff: preserve shared-frag marker during coalescing

skb_try_coalesce() can attach paged frags from @from to @to.  If @from
has SKBFL_SHARED_FRAG set, the resulting @to skb can contain the same
externally-owned or page-cache-backed frags, but the shared-frag marker
is currently lost.

That breaks the invariant relied on by later in-place writers.  In
particular, ESP input checks skb_has_shared_frag() before deciding
whether an uncloned nonlinear skb can skip skb_cow_data().  If TCP
receive coalescing has moved shared frags into an unmarked skb, ESP can
see skb_has_shared_frag() as false and decrypt in place over page-cache
backed frags.

Propagate SKBFL_SHARED_FRAG when skb_try_coalesce() transfers paged
frags.  The tailroom copy path does not need the marker because it copies
bytes into @to's linear data rather than transferring frag descriptors.

## References
- http://www.openwall.com/lists/oss-security/2026/05/13/5
- http://www.openwall.com/lists/oss-security/2026/05/21/11
- http://www.openwall.com/lists/oss-security/2026/05/21/12
- http://www.openwall.com/lists/oss-security/2026/05/21/13
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2f2b16022a2e10ca7bccfb98db5ed2ec0f72641c
- https://git.kernel.org/stable/c/3599e6b3cc1ada96883d496a50a210d3afbb6987
- https://git.kernel.org/stable/c/3884358a9286b17f389a72b1426fc4547c23c111
- https://git.kernel.org/stable/c/3bd9e113d50034db99d7ef69fd8e5242d15e414a
- https://git.kernel.org/stable/c/760e1addc27ba1a7beb4a0a7e8b3e9ec49e7a34e
- https://git.kernel.org/stable/c/78bf6b6bb19541d19fbda6242e7cfe2c682763c0
- https://git.kernel.org/stable/c/9d3e5fd19fe1063bf607219e8562fbd567b8e8d5
- https://git.kernel.org/stable/c/f84eca5817390257cef78013d0112481c503b4a3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46300.json
- https://access.redhat.com/errata/RHBA-2026:20032
- https://access.redhat.com/errata/RHSA-2026:19521
- https://access.redhat.com/errata/RHSA-2026:19540
- https://access.redhat.com/errata/RHSA-2026:19568
- https://access.redhat.com/errata/RHSA-2026:19569
