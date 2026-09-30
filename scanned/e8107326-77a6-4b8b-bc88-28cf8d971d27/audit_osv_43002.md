# [H] ASoC: SOF: ipc3-control: Use overflow checks in control_update size calc

## Summary
Severity: High
Advisory: CVE-2026-72302
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72302
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc3-control: Use overflow checks in control_update size calc

In sof_ipc3_control_update(), the expected_size calculation uses
firmware-provided cdata->num_elems in arithmetic that could overflow
on 32-bit platforms, wrapping to a small value. This would allow the
cdata->rhdr.hdr.size comparison to pass with mismatched sizes,
potentially leading to out-of-bounds access in snd_sof_update_control.

Use check_mul_overflow() and check_add_overflow() to detect and reject
overflowed size calculations.

## References
- https://git.kernel.org/stable/c/312c7d2ebe696da3f885eee77d52297664e57c53
- https://git.kernel.org/stable/c/6856b3c23b0995eefad5a6142b4365ef70e1fe4a
- https://git.kernel.org/stable/c/711d912b18763af62a63aa8f2419a774eb63bba4
- https://git.kernel.org/stable/c/8791977d7289f6e9d2b014f60a5455f053a7bc04
- https://git.kernel.org/stable/c/89a2309a9eec80d4c19e3aed62c4f923594d1911
- https://git.kernel.org/stable/c/ffd79e77f2fbacd7a5d40ad1d4c7f3f089a8f2f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72302.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
