# [M] wifi: cfg80211: fix memory leak in query_regdb_file()

## Summary
Severity: Medium
Advisory: CVE-2022-49881
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49881
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: fix memory leak in query_regdb_file()

In the function query_regdb_file() the alpha2 parameter is duplicated
using kmemdup() and subsequently freed in regdb_fw_cb(). However,
request_firmware_nowait() can fail without calling regdb_fw_cb() and
thus leak memory.

## References
- https://git.kernel.org/stable/c/0ede1a988299e95d54bd89551fd635980572e920
- https://git.kernel.org/stable/c/219446396786330937bcd382a7bc4ccd767383bc
- https://git.kernel.org/stable/c/38c9fa2cc6bf4b6e1a74057aef8b5cffd23d3264
- https://git.kernel.org/stable/c/57b962e627ec0ae53d4d16d7bd1033e27e67677a
- https://git.kernel.org/stable/c/e1e12180321f416d83444f2cdc9259e0f5093d35
- https://git.kernel.org/stable/c/e9b5a4566d5bc71cc901be50d1fa24da00613120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49881.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
