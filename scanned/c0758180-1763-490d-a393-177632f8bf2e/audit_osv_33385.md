# [C] net: qlogic/qede: fix potential out-of-bounds read in qede_tpa_cont() and qede_tpa_end()

## Summary
Severity: Critical
Advisory: CVE-2025-40252
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40252
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qlogic/qede: fix potential out-of-bounds read in qede_tpa_cont() and qede_tpa_end()

The loops in 'qede_tpa_cont()' and 'qede_tpa_end()', iterate
over 'cqe->len_list[]' using only a zero-length terminator as
the stopping condition. If the terminator was missing or
malformed, the loop could run past the end of the fixed-size array.

Add an explicit bound check using ARRAY_SIZE() in both loops to prevent
a potential out-of-bounds access.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/896f1a2493b59beb2b5ccdf990503dbb16cb2256
- https://git.kernel.org/stable/c/917a9d02182ac8b4f25eb47dc02f3ec679608c24
- https://git.kernel.org/stable/c/a778912b4a53587ea07d85526d152f85d109cbfe
- https://git.kernel.org/stable/c/e441db07f208184e0466abf44b389a81d70c340e
- https://git.kernel.org/stable/c/ecbb12caf399d7cf364b7553ed5aebeaa2f255bc
- https://git.kernel.org/stable/c/f0923011c1261b33a2ac1de349256d39cb750dd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40252.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40252
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
