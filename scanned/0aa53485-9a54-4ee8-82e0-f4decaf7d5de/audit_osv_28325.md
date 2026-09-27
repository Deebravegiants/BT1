# [M] Limited file write in Stable-diffusion-webui - GHSL-2024-010

## Summary
Severity: Medium
Advisory: CVE-2024-31462
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-12
Source: https://osv.dev/vulnerability/CVE-2024-31462
Type: osv

## Details
stable-diffusion-webui is a web interface for Stable Diffusion, implemented using Gradio library. Stable-diffusion-webui 1.7.0 is vulnerable to a limited file write affecting Windows systems. The create_ui method (Backup/Restore tab) in modules/ui_extensions.py takes user input into the config_save_name variable on line 653. This user input is later used in the save_config_state method and used to create a file path on line 65, which is afterwards opened for writing on line 67, which leads to a limited file write exploitable on Windows systems. This issue may lead to limited file write. It allows for writing json files anywhere on the server where the web server has access.

## References
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/ui_extensions.py#L59
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/ui_extensions.py#L646-L660
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/ui_extensions.py#L65
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/ui_extensions.py#L653
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/ui_extensions.py#L67
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.7.0/modules/ui_extensions.py
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions/15461
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31462.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31462
- https://securitylab.github.com/advisories/GHSL-2024-010_stable-diffusion-webui
- https://securitylab.github.com/advisories/GHSL-2024-010_stable-diffusion-webui/
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/commit/d9708c92b444894bce8070e4dcfaa093f8eb8d43
