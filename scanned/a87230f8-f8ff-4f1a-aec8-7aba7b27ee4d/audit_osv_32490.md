# [C] Fooocus webui vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-31114
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2025-31114
Type: osv

## Details
Fooocus is an image generating software. In versions 2.5.5 and prior, the Fooocus web UI is vulnerable to remote code execution due to the unsafe use of eval when processing metadata JSON. An attacker with access to the Fooocus web UI may be able to execute arbitrary code on the instance. As of time of publication, no known patched versions are available, but a suggested fix pull request is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31114.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-31114
- https://securitylab.github.com/advisories/GHSL-2024-196_Fooocus/
- https://github.com/lllyasviel/Fooocus/issues/3552
- https://github.com/lllyasviel/Fooocus/pull/4207
