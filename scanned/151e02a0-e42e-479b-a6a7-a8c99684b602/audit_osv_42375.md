# [C] FUXA: Unauthenticated guest JWT bypasses Node-RED secure-mode authorization gate (Remote Script Execution)

## Summary
Severity: Critical
Advisory: CVE-2026-67443
Aliases: GHSA-5h5x-9h7x-23f4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-67443
Type: osv

## Details
FUXA is a web-based Process Visualization (SCADA/HMI/Dashboard) software. In 1.3.2 and earlier, the allowDashboard authorization gate in server/integrations/node-red/index.js calls authJwt.verify for /nodered without inspecting the decoded identity. When nodeRedEnabled is true, secureEnabled is true, and nodeRedAuthMode is secure, a remote unauthenticated attacker can obtain a signed guest token from POST /api/heartbeat and use it to access the RED.httpAdmin editor and flow deployment API. Because the Node-RED configuration has no second adminAuth gate, the attacker can deploy function nodes or invoke fuxa.runScript and runtime.scriptsMgr.runScript, gaining control of FUXA project data, configuration, scripts, filesystem-capable runtime helpers, and potentially operating-system commands when nodeRedUnsafeModules is enabled. This issue is fixed in version 1.3.3.

## References
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67443.json
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-5h5x-9h7x-23f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-67443
- https://github.com/frangoteam/FUXA/commit/e0b553cddb55613b890341270eb17eb586f8cab5
- https://github.com/frangoteam/FUXA/pull/2393
