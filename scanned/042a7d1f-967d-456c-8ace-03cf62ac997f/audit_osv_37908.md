# [M] Wazuh: Unauthenticated cluster packet length leads to uncontrolled memory allocation (remote DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-33754
Aliases: GHSA-476v-28pp-5wg9
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-33754
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. In versions 3.9.0 and above, prior to 4.14.5, a remote attacker can trigger memory exhaustion in the cluster protocol parser by sending a crafted message header with an arbitrarily large payload length. The length is trusted before authentication/decryption and used directly to allocate memory, allowing unauthenticated denial of service of the cluster service. This issue has been fixed in version 4.14.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33754.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-476v-28pp-5wg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33754
