# [C] Hugo 0.162.0 to 0.164.x - Node Permission Model Bypass via Default TailwindCSS Child-Process Grant

## Summary
Severity: Critical
Advisory: CVE-2026-75926
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75926
Type: osv

## Details
Hugo 0.161.0 placed the Node asset pipelines behind the Node.js permission model so that code running through PostCSS, Babel, or TailwindCSS could not reach the file system outside the project directory. Hugo 0.162.0 added tailwindcss to the AllowChildProcess default in config/security/securityConfig.go, which makes nodePermissionArgs in common/hexec/exec.go append --allow-child-process whenever the tool being launched is named tailwindcss. TailwindCSS loads the site's tailwind.config.js through require at startup, so top-level code in that file executes inside the permitted Node process and can call child_process to spawn a shell. The spawned process is not a Node process and inherits none of the permission flags, so it runs with the full privileges of the account performing the build. Building a site whose theme, module, or starter template supplies the Tailwind configuration therefore yields arbitrary command execution rather than the confined file access the permission model was introduced to enforce. Hugo 0.165.0 removes tailwindcss from the default security.exec.allow list, so the tool is no longer launched under the default configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75926.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75926
- https://www.vulncheck.com/advisories/hugo-to-x-node-permission-model-bypass-via-default-tailwindcss-child-process-grant
- https://github.com/gohugoio/hugo/issues/15178
- https://github.com/gohugoio/hugo/commit/8a55df7af2e6da31297245cc54fa2e3b521d93e8
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/blob/v0.164.0/common/hexec/exec.go#L292-L295
- https://github.com/gohugoio/hugo/blob/v0.164.0/config/security/securityConfig.go#L72-L79
