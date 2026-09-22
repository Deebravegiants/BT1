# [C] Flowise before 3.1.3 Sandbox Escape via Puppeteer

## Summary
Severity: Critical
Advisory: CVE-2026-73483
Aliases: GHSA-9gvv-qjj3-2p6g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73483
Type: osv

## Details
Flowise (packages flowise and flowise-components) in versions <= 3.1.2 contain a sandbox escape in the vm2/@flowiseai/nodevm JavaScript sandbox. An authenticated user with access to the /api/v1/node-custom-function endpoint can escape the sandbox by supplying attacker-controlled executablePath and args parameters to puppeteer.launch(), which internally invokes child_process.spawn() outside the sandbox boundary. This allows execution of arbitrary OS commands as the Flowise process user (root in the official Docker image) and arbitrary host file disclosure via Chromium's file:// URL handling. In versions 3.0.8–3.1.2 exploitation requires ALLOW_BUILTIN_DEP=true; earlier versions are exploitable by default. Fixed in 3.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73483.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-9gvv-qjj3-2p6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73483
- https://www.vulncheck.com/advisories/flowise-before-sandbox-escape-via-puppeteer
