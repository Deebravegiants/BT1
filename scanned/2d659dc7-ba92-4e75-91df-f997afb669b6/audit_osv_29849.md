# [M] OSS Endpoint Manager allows unauthorized access to read system files

## Summary
Severity: Medium
Advisory: CVE-2024-47071
Aliases: GHSA-x9wc-qjrc-j7ww
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-47071
Type: osv

## Details
OSS Endpoint Manager is an endpoint manager module for FreePBX. OSS Endpoint Manager module activation can allow authenticated web users unauthorized access to read system files with the permissions of the webserver process. This vulnerability is fixed in 14.0.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47071.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-x9wc-qjrc-j7ww
- https://nvd.nist.gov/vuln/detail/CVE-2024-47071
- https://github.com/FreePBX-ContributedModules/endpointman/commit/bad70ca3de2166bbd24f273f7f212a8b2c92a719
