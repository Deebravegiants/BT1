# [C] NetBox 4.3.5 - 4.5.4 RCE via RenderTemplateMixin

## Summary
Severity: Critical
Advisory: CVE-2026-29514
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-29514
Type: osv

## Details
NetBox versions 4.3.5 through 4.5.4 contain a remote code execution vulnerability in the RenderTemplateMixin.get_environment_params() method that allows authenticated users with exporttemplate or configtemplate permissions to execute arbitrary code by specifying malicious Python callables in the environment_params field. Attackers can bypass Jinja2 SandboxedEnvironment protections by setting the finalize parameter to any importable Python callable such as subprocess.getoutput, which is invoked on every rendered expression outside the sandbox's call interception mechanism, achieving remote code execution as the NetBox service user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29514.json
- https://github.com/netbox-community/netbox/releases/tag/v4.6.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-29514
- https://www.vulncheck.com/advisories/netbox-rce-via-rendertemplatemixin
- https://github.com/netbox-community/netbox/issues/22079
- https://github.com/netbox-community/netbox/pull/22078
- https://github.com/netbox-community/netbox/pull/22170
- https://github.com/netbox-community/netbox/commit/d124c5fe86e12aad61285133c0caf16adcda8f2e
- https://chocapikk.com/posts/2026/netbox-export-template-rce/
