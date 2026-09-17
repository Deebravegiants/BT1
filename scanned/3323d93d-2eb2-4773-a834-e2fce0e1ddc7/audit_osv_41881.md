# [C] igc: set tx buffer type for SMD frames

## Summary
Severity: Critical
Advisory: CVE-2026-64035
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64035
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

igc: set tx buffer type for SMD frames

Sashiko pointed out that igc_fpe_init_smd_frame() initializes
igc_tx_buffer fields for an SMD skb, but does not set the buffer type:
https://sashiko.dev/#/patchset/20260415025226.114115-1-kohei%40enjuk.jp

Since igc_tx_buffer entries are reused, a stale XDP or XSK type can
remain and make TX completion use the wrong cleanup path.

Set the buffer type to IGC_TX_BUFFER_TYPE_SKB.

## References
- https://git.kernel.org/stable/c/1c8587bd025244aa52061f5ceecbf5e68a1063d9
- https://git.kernel.org/stable/c/1f83545f432d106d5fc71d3997b2d382104ebcc4
- https://git.kernel.org/stable/c/5acc641e590e008caaed480ed9ffae47cf7ecbdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64035.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64035
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
