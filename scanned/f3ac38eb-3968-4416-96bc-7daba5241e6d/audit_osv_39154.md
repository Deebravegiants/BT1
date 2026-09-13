# [M] Wazuh : size_t underflow in msgs.c ReadSecMSG causes wazuh-remoted DoS and potential heap overflow via crafted agent message

## Summary
Severity: Medium
Advisory: CVE-2026-44251
Aliases: GHSA-jv5r-5p7c-g9fq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-44251
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. In versions 3.0.0 and above, prior to 4.14.5, a size_t integer underflow in os_crypto/shared/msgs.c:389 allows any enrolled Wazuh agent to crash the wazuh-remoted process on the manager, immediately disconnecting all agents from the manager. A second code path reached by the same underflow may allow heap memory corruption. This issue has been fixed in version 4.14.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44251.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-jv5r-5p7c-g9fq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44251
