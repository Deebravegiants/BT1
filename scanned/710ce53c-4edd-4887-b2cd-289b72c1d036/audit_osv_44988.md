# [C] Nango < 0.71.6 Missing Authentication RCE via runner tRPC server

## Summary
Severity: Critical
Advisory: CVE-2026-9317
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-9317
Type: osv

## Details
Nango before 0.71.6 contains a missing authentication vulnerability in the runner tRPC server that allows unauthenticated attackers to execute arbitrary JavaScript code by invoking the exposed start procedure without credentials. Attackers with network access to the runner port can send requests to the unauthenticated start procedure, bypassing the unenforced RUNNER_SECRET_KEY environment variable, to achieve remote code execution within the runner process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9317.json
- https://github.com/NangoHQ/nango/releases/tag/v0.71.6
- https://nvd.nist.gov/vuln/detail/CVE-2026-9317
- https://www.vulncheck.com/advisories/nango-missing-authentication-rce-via-runner-trpc-server
- https://github.com/NangoHQ/nango/commit/ed3030a9a0f8e4f3810fd10cb3a1905a2f5f87d2
- https://github.com/NangoHQ/nango/pull/7288
- https://github.com/NangoHQ/nango
