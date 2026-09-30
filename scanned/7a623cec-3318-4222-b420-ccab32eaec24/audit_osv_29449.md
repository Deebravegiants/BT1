# [M] ESP-NOW Replay Attacks Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-42483
Aliases: GHSA-wf6q-c2xr-77xj
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-42483
Type: osv

## Details
ESP-NOW Component provides a connectionless Wi-Fi communication protocol. An replay attacks vulnerability was discovered in the implementation of the ESP-NOW because the caches is not differentiated by message types, it is a single, shared resource for all kinds of messages, whether they are broadcast or unicast, and regardless of whether they are ciphertext or plaintext. This can result an attacker to clear the cache of its legitimate entries, there by creating an opportunity to re-inject previously captured packets. This vulnerability is fixed in 2.5.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42483.json
- https://github.com/espressif/esp-now/security/advisories/GHSA-wf6q-c2xr-77xj
- https://nvd.nist.gov/vuln/detail/CVE-2024-42483
- https://github.com/espressif/esp-now/commit/4e30db50d541b2909d278ef0db05de1a3d7190ef
