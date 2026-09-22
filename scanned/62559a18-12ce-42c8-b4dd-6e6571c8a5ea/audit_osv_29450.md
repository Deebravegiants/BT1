# [M] ESP-NOW OOB Vulnerability In Group Type Message

## Summary
Severity: Medium
Advisory: CVE-2024-42484
Aliases: GHSA-q6f6-4qc5-vhx5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-42484
Type: osv

## Details
ESP-NOW Component provides a connectionless Wi-Fi communication protocol. An Out-of-Bound (OOB) vulnerability was discovered in the implementation of the ESP-NOW group type message because there is no check for the addrs_num field of the group type message. This can result in memory corruption related attacks. Normally there are two fields in the group information that need to be checked, i.e., the addrs_num field and the addrs_list fileld. Since we only checked the addrs_list field, an attacker can send a group type message with an invalid addrs_num field, which will cause the message handled by the firmware to be much larger than the current buffer, thus causing a memory corruption issue that goes beyond the payload length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42484.json
- https://github.com/espressif/esp-now/security/advisories/GHSA-q6f6-4qc5-vhx5
- https://nvd.nist.gov/vuln/detail/CVE-2024-42484
- https://github.com/espressif/esp-now/commit/b03a1b4593713fa4bf0038a87edca01f10114a7a
