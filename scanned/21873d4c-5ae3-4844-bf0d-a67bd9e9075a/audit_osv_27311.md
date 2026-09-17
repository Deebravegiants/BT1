# [H] Bluetooth characteristic LESC security requirement not enforced without additional flags

## Summary
Severity: High
Advisory: CVE-2024-1638
Aliases: GHSA-p6f3-f63q-5mc2
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-1638
Type: osv

## Details
The documentation specifies that the BT_GATT_PERM_READ_LESC and BT_GATT_PERM_WRITE_LESC defines for a Bluetooth characteristic: Attribute read/write permission with LE Secure Connection encryption. If set, requires that LE Secure Connections is used for read/write access, however this is only true when it is combined with other permissions, namely BT_GATT_PERM_READ_ENCRYPT/BT_GATT_PERM_READ_AUTHEN (for read) or BT_GATT_PERM_WRITE_ENCRYPT/BT_GATT_PERM_WRITE_AUTHEN (for write), if these additional permissions are not set (even in secure connections only mode) then the stack does not perform any permission checks on these characteristics and they can be freely written/read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1638.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-p6f3-f63q-5mc2
- https://nvd.nist.gov/vuln/detail/CVE-2024-1638
- https://github.com/zephyrproject-rtos/zephyr
