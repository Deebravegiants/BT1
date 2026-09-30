# [C] Hashgraph Guardian 3.5.1 Unsandboxed JavaScript Execution RCE

## Summary
Severity: Critical
Advisory: CVE-2026-39911
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39911
Type: osv

## Details
Hashgraph Guardian through version 3.5.1, fixed in commit 45fbe2f, contains an unsandboxed JavaScript execution vulnerability in the Custom Logic policy block worker that allows authenticated Standard Registry users to execute arbitrary code by passing user-supplied JavaScript expressions directly to the Node.js Function() constructor without isolation. Attackers can import native Node.js modules to read arbitrary files from the container filesystem, access process environment variables containing sensitive credentials such as RSA private keys, JWT signing keys, and API tokens, and forge valid authentication tokens for any user including administrators.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39911.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39911
- https://www.vulncheck.com/advisories/hashgraph-guardian-unsandboxed-javascript-execution-rce
- https://github.com/hashgraph/guardian/pull/5929
- https://github.com/hashgraph/guardian/commit/45fbe2f7e0e8feee30105d42d66ed63fb6177ebe
- https://github.com/hashgraph/guardian
