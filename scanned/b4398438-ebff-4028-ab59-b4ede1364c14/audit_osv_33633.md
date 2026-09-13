# [M] Nextcloud Server's test remote endpoint is not rate limited

## Summary
Severity: Medium
Advisory: CVE-2025-47791
Aliases: GHSA-c7vq-m7f8-rx37
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-47791
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. In Nextcloud Server prior to 28.0.13, 29.0.10, and 30.0.3 and Nextcloud Enterprise Server prior to 28.0.13, 29.0.10, and 30.0.3, a currently unused endpoint to verify a share recipient was not protected correctly, allowing to proxy requests to another server. The endpoint was removed in Nextcloud Server 28.0.13, 29.0.10, and 30.0.3 and Nextcloud Enterprise Server 28.0.13, 29.0.10, and 30.0.3. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47791.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-c7vq-m7f8-rx37
- https://nvd.nist.gov/vuln/detail/CVE-2025-47791
- https://github.com/nextcloud/server/pull/49558
