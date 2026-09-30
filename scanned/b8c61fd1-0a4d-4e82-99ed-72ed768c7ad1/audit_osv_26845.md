# [H] sfc: fix crash when reading stats while NIC is resetting

## Summary
Severity: High
Advisory: CVE-2023-54156
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54156
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: fix crash when reading stats while NIC is resetting

efx_net_stats() (.ndo_get_stats64) can be called during an ethtool
 selftest, during which time nic_data->mc_stats is NULL as the NIC has
 been fini'd.  In this case do not attempt to fetch the latest stats
 from the hardware, else we will crash on a NULL dereference:
    BUG: kernel NULL pointer dereference, address: 0000000000000038
    RIP efx_nic_update_stats
    abridged calltrace:
    efx_ef10_update_stats_pf
    efx_net_stats
    dev_get_stats
    dev_seq_printf_stats
Skipping the read is safe, we will simply give out stale stats.
To ensure that the free in efx_ef10_fini_nic() does not race against
 efx_ef10_update_stats_pf(), which could cause a TOCTTOU bug, take the
 efx->stats_lock in fini_nic (it is already held across update_stats).

## References
- https://git.kernel.org/stable/c/446f5567934331923d0aec4ce045e4ecb0174aae
- https://git.kernel.org/stable/c/470152d76b3ed107d172ea46acc4bfa941f20b4b
- https://git.kernel.org/stable/c/91f4ef204e731565afdc6c2a7fcf509a3fd6fd67
- https://git.kernel.org/stable/c/aba32b4c58112960c0c708703ca6b44dc8944082
- https://git.kernel.org/stable/c/cb1aa7cc562cab6a87ea33574c8c65f2d2fd7aeb
- https://git.kernel.org/stable/c/d1b355438b8325a486f087e506d412c4e852f37b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54156.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
