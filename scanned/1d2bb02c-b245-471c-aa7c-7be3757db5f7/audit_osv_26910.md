# [M] Potential buffer overflow vulnerabilities in the Zephyr Bluetooth subsystem

## Summary
Severity: Medium
Advisory: CVE-2023-5753
Aliases: GHSA-hmpr-px56-rvww
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-10-24
Source: https://osv.dev/vulnerability/CVE-2023-5753
Type: osv

## Details
Potential buffer overflows in the Bluetooth subsystem due to asserts being disabled in /subsys/bluetooth/host/hci_core.c

## References
- http://packetstormsecurity.com/files/175657/Zephyr-RTOS-3.x.0-Buffer-Overflows.html
- http://seclists.org/fulldisclosure/2023/Nov/1
- http://www.openwall.com/lists/oss-security/2023/11/07/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5753.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-hmpr-px56-rvww
- https://nvd.nist.gov/vuln/detail/CVE-2023-5753
- https://github.com/zephyrproject-rtos/zephyr
