# [H] wifi: ath12k: fix inconsistent arvif state in vdev_create error paths

## Summary
Severity: High
Advisory: CVE-2026-74367
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74367
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix inconsistent arvif state in vdev_create error paths

ath12k_mac_vdev_create() has three error path issues that leave arvif
in an inconsistent state:

1. When ath12k_wmi_vdev_create() fails, the function returns directly
   without clearing arvif->ar, which was already set before the WMI
   call. Subsequent code checking arvif->ar to determine vdev readiness
   will see a non-NULL value despite no vdev existing in firmware.

2. When ath12k_wmi_send_peer_delete_cmd() fails in err_peer_del, the
   code jumped to err: skipping the DP peer cleanup and vdev rollback,
   leaving num_created_vdevs, vdev maps and arvif list membership live.

3. When ath12k_wait_for_peer_delete_done() fails, the code jumped to
   err_vdev_del: skipping the DP peer cleanup.

Fix by changing the ath12k_wmi_vdev_create() failure to goto err instead
of returning directly, routing both err_peer_del failure paths through
err_dp_peer_del: for proper DP peer and vdev rollback, and consolidating
the arvif state cleanup at err:.

Tested-on: WCN7850 hw2.0 PCI WLAN.HMT.1.1.c5-00302-QCAHMTSWPL_V1.0_V2.0_SILICONZ-1.115823.3

## References
- https://git.kernel.org/stable/c/c972636efc63f0f43d725b59805dd1ae5bc4b31e
- https://git.kernel.org/stable/c/e0140e094b196d92f2a4ce167ee73cbfab000290
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
