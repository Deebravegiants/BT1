# [C] vm2: Sandbox Escape

## Summary
Severity: Critical
Advisory: CVE-2026-47131
Aliases: GHSA-v6mx-mf47-r5wg
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47131
Type: osv

## Details
vm2 is an open source vm/sandbox for Node.js. Prior to version 3.11.4, by combining Buffer.call.call({}.__lookupGetter__, Buffer, "__proto__"), Buffer.call.call({}.__lookupSetter__, Buffer, "__proto__"), and Node.js's ERR_INVALID_ARG_TYPE Error, the host's TypeError constructor can be obtained, which allows the escape from the sandbox. This allows attackers to run arbitrary code. This issue has been patched in version 3.11.4.

## References
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47131.json
- https://github.com/patriksimek/vm2/security/advisories/GHSA-v6mx-mf47-r5wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47131
- https://github.com/patriksimek/vm2/commit/27c525f4615e2b983f122e2bed327d810126f5c8
