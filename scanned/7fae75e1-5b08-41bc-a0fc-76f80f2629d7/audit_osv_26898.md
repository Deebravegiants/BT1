# [H] CVE-2023-5563

## Summary
Severity: High
Advisory: CVE-2023-5563
Aliases: GHSA-98mc-rj7w-7rpv
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-10-12
Source: https://osv.dev/vulnerability/CVE-2023-5563
Type: osv

## Details
The SJA1000 CAN controller driver backend automatically attempt to recover from a bus-off event when built with CONFIG_CAN_AUTO_BUS_OFF_RECOVERY=y. This results in calling k_sleep() in IRQ context, causing a fatal exception.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5563.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-98mc-rj7w-7rpv
- https://nvd.nist.gov/vuln/detail/CVE-2023-5563
- https://github.com/zephyrproject-rtos/zephyr
