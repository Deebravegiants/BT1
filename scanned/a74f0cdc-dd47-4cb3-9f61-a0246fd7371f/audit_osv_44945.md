# [C] knowns through 0.33.0 Path Traversal via Template Engine

## Summary
Severity: Critical
Advisory: CVE-2026-88937
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88937
Type: osv

## Details
knowns through 0.33.0 fails to properly validate template destination paths in the code generation template engine, allowing attackers to read and write arbitrary files outside the project root. Attackers can supply malicious templates that traverse directories to overwrite shell profiles, steal credentials, or achieve persistent code execution on victim systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88937.json
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-68cq-4rwm-f7jr
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-xjcg-5j3r-m6f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-88937
- https://www.vulncheck.com/advisories/knowns-through-0.33.0-path-traversal-via-template-engine
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/codegen/template_engine.go#L318-L344
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/codegen/template_engine.go#L625-L636
