# [M] Stable Diffusion WebUI Credential Disclosure via /sdapi/v1/cmd-flags

## Summary
Severity: Medium
Advisory: CVE-2026-82288
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82288
Type: osv

## Details
Stable Diffusion WebUI through 1.10.1 contains a credential disclosure vulnerability in the /sdapi/v1/cmd-flags endpoint that returns parsed command-line arguments including gradio_auth and api_auth values in cleartext. Unauthenticated attackers can access this endpoint to retrieve configured usernames and passwords, then use them to authenticate to the interface and access the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82288
- https://www.vulncheck.com/advisories/stable-diffusion-webui-credential-disclosure-via-sdapi-v1-cmd-flags
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17411
- https://github.com/AUTOMATIC1111/stable-diffusion-webui
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/82a973c04367123ae98bd9abdf80d9eda9b910e2/modules/api/api.py
