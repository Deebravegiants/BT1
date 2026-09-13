# [H] wifi: iwlwifi: fix 22000 series SMEM parsing

## Summary
Severity: High
Advisory: CVE-2026-43172
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43172
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: fix 22000 series SMEM parsing

If the firmware were to report three LMACs (which doesn't
exist in hardware) then using "fwrt->smem_cfg.lmac[2]" is
an overrun of the array. Reject such and use IWL_FW_CHECK
instead of WARN_ON in this function.

## References
- https://git.kernel.org/stable/c/1d49a42717bdc8de77eabeb5b7d3e88d141ffea9
- https://git.kernel.org/stable/c/2b4b1510aaaf5b9fb57327ecffc20c055f61f205
- https://git.kernel.org/stable/c/58192b9ce09b0f0f86e2036683bd542130b91a98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
