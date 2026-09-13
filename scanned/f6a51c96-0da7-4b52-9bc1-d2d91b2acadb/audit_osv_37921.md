# [C] Windmill: Rogue Workspace Admins can inject code via unescaped workspace environment variable interpolation in NativeTS executor

## Summary
Severity: Critical
Advisory: CVE-2026-33881
Aliases: GHSA-8q8j-mm3g-5c2q
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33881
Type: osv

## Details
Windmill is an open-source developer platform for internal code: APIs, background jobs, workflows and UIs. Workspace environment variable values are interpolated into JavaScript string literals without escaping single quotes in the NativeTS executor. A workspace admin who sets a custom environment variable with a value containing `'` can inject arbitrary JavaScript that executes inside every NativeTS script in that workspace. This is a code injection bug in `worker.rs`, not related to the sandbox/NSJAIL topic. Version 1.664.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33881.json
- https://github.com/windmill-labs/windmill/security/advisories/GHSA-8q8j-mm3g-5c2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33881
