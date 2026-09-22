# [H] Espressif Shared GitHub DangerJS: Untrusted Search Path in DangerJS Action Entrypoint

## Summary
Severity: High
Advisory: CVE-2026-44358
Aliases: GHSA-wm3p-pv54-6w73
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-44358
Type: osv

## Details
Espressif Shared GitHub DangerJS is a reusable GitHub Action CI DangerJS workflow for Espressif GitHub projects. Prior to 1.0.1, the action's entrypoint.sh invoked DangerJS from the caller's workspace after copying the fork's checkout into it, creating an untrusted search path for both binary resolution and Node.js module resolution. A fork pull request processed by a pull_request_target workflow could therefore cause fork-supplied code to execute inside the action container in place of the action's own code. This vulnerability is fixed in 1.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44358.json
- https://github.com/espressif/shared-github-dangerjs/security/advisories/GHSA-wm3p-pv54-6w73
- https://nvd.nist.gov/vuln/detail/CVE-2026-44358
- https://github.com/espressif/shared-github-dangerjs/commit/d742408028135ea200982b5b2e3e438dc4e5a25d
