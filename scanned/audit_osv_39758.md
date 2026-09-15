# [C] vm2: Sandbox Breakout Using Promise Species

## Summary
Severity: Critical
Advisory: CVE-2026-47208
Aliases: GHSA-76w7-j9cq-rx2j
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47208
Type: osv

## Details
vm2 is an open source vm/sandbox for Node.js. Prior to version 3.11.4, VM2 suffers from a sandbox breakout vulnerability. This allows attackers to write code which can escape from the VM2 sandbox and execute arbitrary commands on the host system. This issue has been patched in version 3.11.4.

## References
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47208.json
- https://github.com/patriksimek/vm2/security/advisories/GHSA-76w7-j9cq-rx2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-47208
- https://github.com/patriksimek/vm2/commit/a462655009669c3124ee39498121651597529ea8
