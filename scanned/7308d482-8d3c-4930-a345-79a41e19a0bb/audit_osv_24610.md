# [M] reason-jose ignores signature checks

## Summary
Severity: Medium
Advisory: CVE-2023-23928
Aliases: GHSA-7jj9-6qwv-wpm7
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2023-02-01
Source: https://osv.dev/vulnerability/CVE-2023-23928
Type: osv

## Details
reason-jose is a JOSE implementation in ReasonML and OCaml.`Jose.Jws.validate` does not check HS256 signatures. This allows tampering of JWS header and payload data if the service does not perform additional checks. Such tampering could expose applications using reason-jose to authorization bypass. Applications relying on JWS claims assertion to enforce security boundaries may be vulnerable to privilege escalation. This issue has been patched in version 0.8.2.

## References
- https://github.com/ulrikstrid/reason-jose/releases/tag/v0.8.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23928.json
- https://github.com/ulrikstrid/reason-jose/security/advisories/GHSA-7jj9-6qwv-wpm7
- https://nvd.nist.gov/vuln/detail/CVE-2023-23928
- https://github.com/ulrikstrid/reason-jose/commit/36cd724db3cbec121757624da49072386bd869e5
