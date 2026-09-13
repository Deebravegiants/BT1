# [M] zsa Generates Error Messages Containing Sensitive Information

## Summary
Severity: Medium
Advisory: CVE-2024-37162
Aliases: GHSA-wjmj-h3xc-hxp8
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-06-07
Source: https://osv.dev/vulnerability/CVE-2024-37162
Type: osv

## Details
zsa is a library for building typesafe server actions in Next.js. All users are impacted. The zsa application transfers the parse error stack from the server to the client in production build mode. This can potentially reveal sensitive information about the server environment, such as the machine username and directory paths. An attacker could exploit this vulnerability to gain unauthorized access to sensitive server information. This information could be used to plan further attacks or gain a deeper understanding of the server infrastructure. This has been patched on `0.3.3`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37162.json
- https://github.com/IdoPesok/zsa/security/advisories/GHSA-wjmj-h3xc-hxp8
- https://nvd.nist.gov/vuln/detail/CVE-2024-37162
- https://github.com/IdoPesok/zsa/commit/86b86b282bde6780963f62406cc8bc65f2c86f3a
