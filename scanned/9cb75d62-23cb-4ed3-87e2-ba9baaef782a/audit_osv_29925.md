# [H] wifi: rtw89: remove unused C2H event ID RTW89_MAC_C2H_FUNC_READ_WOW_CAM to prevent out-of-bounds reading

## Summary
Severity: High
Advisory: CVE-2024-47721
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47721
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: remove unused C2H event ID RTW89_MAC_C2H_FUNC_READ_WOW_CAM to prevent out-of-bounds reading

The handler of firmware C2H event RTW89_MAC_C2H_FUNC_READ_WOW_CAM isn't
implemented, but driver expects number of handlers is
NUM_OF_RTW89_MAC_C2H_FUNC_WOW causing out-of-bounds access. Fix it by
removing ID.

Addresses-Coverity-ID: 1598775 ("Out-of-bounds read")

## References
- https://git.kernel.org/stable/c/10463308b9454f534d03300cf679bc4b3d078f46
- https://git.kernel.org/stable/c/2c9c2d1a20916589497a7facbea3e82cabec4ab8
- https://git.kernel.org/stable/c/56310ddb50b190b3390fdc974aec455d0a516bd2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47721.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47721
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
