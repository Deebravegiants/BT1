# [H] ServerCo getssl ACME shell script path injection

## Summary
Severity: High
Advisory: CVE-2026-10303
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-10303
Type: osv

## Details
In ServerCo getssl version 2.49 and prior, the ACME challenge token returned to the client was not strictly validated against RFC 8555 before being used in challenge-file handling, allowing a maliciously crafted token to influence local path/filename usage during validation. An attacker who can supply ACME challenge responses to getssl (for example, a malicious or compromised CA endpoint, or an on-path adversary able to tamper with that response path) could exploit this to achieve unauthorized file write/path traversal effects, usually with elevated privileges, ultimately allowing for remote command injection. This issue appears related in spirit to CVE-2023-38198, and is an instance of CWE-73, "External control of file name or path." Other ACME shell script handlers may be affected by similar issues.

## References
- https://remyhax.xyz/posts/reproducing-lawful-tls-wiretapping/
- https://www.cve.org/CVERecord?id=CVE-2023-38198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10303.json
- https://github.com/srvrco/getssl/releases/tag/v2.50
- https://nvd.nist.gov/vuln/detail/CVE-2026-10303
- https://www.runzero.com/advisories/serverco-getssl-acme-cmd-injection-cve-2026-10303/
- https://github.com/srvrco/getssl/pull/896
- https://github.com/srvrco/getssl
