# [M] CVE-2021-47586

## Summary
Severity: Medium
Advisory: CVE-2021-47586
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47586
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: dwmac-rk: fix oob read in rk_gmac_setup

KASAN reports an out-of-bounds read in rk_gmac_setup on the line:

	while (ops->regs[i]) {

This happens for most platforms since the regs flexible array member is
empty, so the memory after the ops structure is being read here.  It
seems that mostly this happens to contain zero anyway, so we get lucky
and everything still works.

To avoid adding redundant data to nearly all the ops structures, add a
new flag to indicate whether the regs field is valid and avoid this loop
when it is not.

## References
- https://git.kernel.org/stable/c/0546b224cc7717cc8a2db076b0bb069a9c430794
- https://git.kernel.org/stable/c/0b4a5d1e15ce72f69be48f38dc0401dab890ae0f
