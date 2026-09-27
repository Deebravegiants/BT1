# [H] ath11k: Change max no of active probe SSID and BSSID to fw capability

## Summary
Severity: High
Advisory: CVE-2022-49533
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49533
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath11k: Change max no of active probe SSID and BSSID to fw capability

The maximum number of SSIDs in a for active probe requests is currently
reported as 16 (WLAN_SCAN_PARAMS_MAX_SSID) when registering the driver.
The scan_req_params structure only has the capacity to hold 10 SSIDs.
This leads to a buffer overflow which can be triggered from
wpa_supplicant in userspace. When copying the SSIDs into the
scan_req_params structure in the ath11k_mac_op_hw_scan route, it can
overwrite the extraie pointer.

Firmware supports 16 ssid * 4 bssid, for each ssid 4 bssid combo probe
request will be sent, so totally 64 probe requests supported. So
set both max ssid and bssid to 16 and 4 respectively. Remove the
redundant macros of ssid and bssid.

Tested-on: IPQ8074 hw2.0 AHB WLAN.HK.2.7.0.1-01300-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/210505788f1d243232e21ef660efcd4838890ce8
- https://git.kernel.org/stable/c/50dc9ce9f80554a88e33b73c30851acf2be36ed3
- https://git.kernel.org/stable/c/ec5dfa1d66f2f71a48dab027d26a9fa78eb0f58f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49533.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
