# [M] soc: qcom: geni-se: fix array underflow in geni_se_clk_tbl_get()

## Summary
Severity: Medium
Advisory: CVE-2024-53158
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53158
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: geni-se: fix array underflow in geni_se_clk_tbl_get()

This loop is supposed to break if the frequency returned from
clk_round_rate() is the same as on the previous iteration.  However,
that check doesn't make sense on the first iteration through the loop.
It leads to reading before the start of these->clk_perf_tbl[] array.

## References
- https://git.kernel.org/stable/c/351bb7f9ecb9d1f09bd7767491a2b8d07f4f1ea4
- https://git.kernel.org/stable/c/37cdd4f0c266560b7b924c42361eeae3dc5f0c3e
- https://git.kernel.org/stable/c/56eda41dcce0ec4d3418b4f85037bdea181486cc
- https://git.kernel.org/stable/c/748557ca7dc94695a6e209eb68fce365da9a3bb3
- https://git.kernel.org/stable/c/78261cb08f06c93d362cab5c5034bf5899bc7552
- https://git.kernel.org/stable/c/7a3465b79ef0539aa10b310ac3cc35e0ae25b79e
- https://git.kernel.org/stable/c/b0a9c6ccaf88c4701787f61ecd2ec0eb014a0677
- https://git.kernel.org/stable/c/c24e019ca12d9ec814af04b30a64dd7173fb20fe
- https://git.kernel.org/stable/c/f4b7bf5a50f1fa25560f0b66a13563465542861b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53158.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
