# [M] CodeWhale before 0.8.64 Environment Variable Leak via js_execution

## Summary
Severity: Medium
Advisory: CVE-2026-75915
Aliases: GHSA-h539-c7r8-3xq4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75915
Type: osv

## Details
CodeWhale versions before 0.8.64 contain an environment variable exposure vulnerability in the js_execution tool that fails to scrub parent process environment variables before spawning Node.js. Attackers can craft malicious JavaScript code executed by the tool to read process.env and leak API keys, cloud credentials, and authentication tokens back to the model context.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75915.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-h539-c7r8-3xq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-75915
- https://www.vulncheck.com/advisories/codewhale-before-environment-variable-leak-via-js-execution
- https://github.com/Hmbown/CodeWhale/commit/26de44a8bd5051f8f944ea60b2c37ae1d2b7d25e
