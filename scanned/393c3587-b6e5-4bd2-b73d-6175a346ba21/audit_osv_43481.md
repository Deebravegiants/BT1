# [M] Wazuh 4.4.0 < 4.14.7 DoS via fdecompress_files() Zip Bomb

## Summary
Severity: Medium
Advisory: CVE-2026-74046
Aliases: GHSA-mr7j-w2m4-vw5j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-74046
Type: osv

## Details
Wazuh 4.4.0 before 4.14.7 contains a denial of service vulnerability in the fdecompress_files() function within cluster.py that allows authenticated cluster peers to exhaust memory by supplying a malicious synchronization archive without decompressed size limits. Attackers holding a valid cluster Fernet key can upload a small, highly compressed zip bomb archive that forces wazuh-clusterd on the master node to decompress the full payload into memory, causing memory exhaustion and service disruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74046.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-mr7j-w2m4-vw5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-74046
- https://www.vulncheck.com/advisories/wazuh-dos-via-fdecompress-files-zip-bomb
- https://github.com/wazuh/wazuh/pull/37119
- https://github.com/wazuh/wazuh
