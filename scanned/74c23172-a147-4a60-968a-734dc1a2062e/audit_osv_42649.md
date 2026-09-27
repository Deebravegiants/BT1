# [C] LAMP 5.6.2 GlueFactory Unsandboxed Groovy Script Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-69100
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-69100
Type: osv

## Details
LAMP Rapid Development Platform through 5.6.2, fixed in commit 84b0c27, contains a remote code execution vulnerability in GlueFactory that executes unsandboxed Groovy scripts from database template fields without compilation restrictions or whitelisting. Attackers can write or influence the script field via message template endpoints to execute arbitrary Groovy code and OS commands on the backend server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69100
- https://www.vulncheck.com/advisories/lamp-gluefactory-unsandboxed-groovy-script-remote-code-execution
- https://github.com/dromara/lamp-cloud/commit/84b0c27d3693e468c2c690d9fbc8ea9c22cd34e3
- https://github.com/dromara/lamp-cloud
- https://github.com/dromara/lamp-cloud/issues/408
