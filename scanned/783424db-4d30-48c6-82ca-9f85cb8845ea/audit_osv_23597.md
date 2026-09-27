# [H] clk: visconti: prevent array overflow in visconti_clk_register_gates()

## Summary
Severity: High
Advisory: CVE-2022-49186
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49186
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: visconti: prevent array overflow in visconti_clk_register_gates()

This code was using -1 to represent that there was no reset function.
Unfortunately, the -1 was stored in u8 so the if (clks[i].rs_id >= 0)
condition was always true.  This lead to an out of bounds access in
visconti_clk_register_gates().

## References
- https://git.kernel.org/stable/c/2723543c1d60278d5aef1c4ad732dbad24b84a81
- https://git.kernel.org/stable/c/c5601e0720ce1a3ad895f94a5838530edde01ed3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49186.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
