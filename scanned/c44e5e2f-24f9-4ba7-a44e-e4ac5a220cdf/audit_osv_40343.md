# [C] netfilter: nfnetlink_osf: fix out-of-bounds read on option matching

## Summary
Severity: Critical
Advisory: CVE-2026-52999
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52999
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_osf: fix out-of-bounds read on option matching

In nf_osf_match(), the nf_osf_hdr_ctx structure is initialized once
and passed by reference to nf_osf_match_one() for each fingerprint
checked. During TCP option parsing, nf_osf_match_one() advances the
shared ctx->optp pointer.

If a fingerprint perfectly matches, the function returns early without
restoring ctx->optp to its initial state. If the user has configured
NF_OSF_LOGLEVEL_ALL, the loop continues to the next fingerprint.
However, because ctx->optp was not restored, the next call to
nf_osf_match_one() starts parsing from the end of the options buffer.
This causes subsequent matches to read garbage data and fail
immediately, making it impossible to log more than one match or logging
incorrect matches.

Instead of using a shared ctx->optp pointer, pass the context as a
constant pointer and use a local pointer (optp) for TCP option
traversal. This makes nf_osf_match_one() strictly stateless from the
caller's perspective, ensuring every fingerprint check starts at the
correct option offset.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0145548346c4a30981a870a8ca00eac46ba27e85
- https://git.kernel.org/stable/c/1c136f2c44a5913646bac85303612fd0825197a0
- https://git.kernel.org/stable/c/1e19a07291bb8682c14c39a64725a3ae54ab8ccc
- https://git.kernel.org/stable/c/21883587593d7c8bb519a79460a0b5bc5ffbdabd
- https://git.kernel.org/stable/c/32e50f92c7cf3f4eba29622179a5fcdc2aebab41
- https://git.kernel.org/stable/c/70a3f31d25cf2ec9d4ddfa408120171ead955623
- https://git.kernel.org/stable/c/edb78a142d2e5948e63647c0646aa7e7886935f0
- https://git.kernel.org/stable/c/f5ca450087c3baf3651055e7a6de92600f827af3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
