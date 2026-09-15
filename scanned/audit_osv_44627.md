# [C] SiYuan before v3.8.2 TLS Private Key Disclosure via getFile

## Summary
Severity: Critical
Advisory: CVE-2026-85175
Aliases: GHSA-4wwp-f6gw-6qm5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85175
Type: osv

## Details
SiYuan versions <= 3.8.1 (fixed in v3.8.2) contain an incomplete blocklist in the IsForbiddenAbsPath() function (kernel/util/path_guard.go), which only blocks conf/conf.json by exact match and does not restrict the TLS private key (conf/key.pem) or CA private key (conf/ca.key) stored in the same conf/ directory. Because the getFile handler skips the blocklist for RoleAdministrator and all authenticated users receive RoleAdministrator in v3.8.1, any user (or any client on a default no-auth-code instance) can retrieve these private keys via POST /api/file/getFile. On deployments with TLS enabled, this allows decryption of captured HTTPS traffic (key.pem) and forging of certificates trusted by clients that imported SiYuan's CA (ca.key).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85175.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-4wwp-f6gw-6qm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-85175
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-tls-private-key-disclosure-via-getfile
