# [M] gpt_academic's Configuration File vulnerable to File Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2023-33979
Aliases: GHSA-pg65-p24m-wf5g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-31
Source: https://osv.dev/vulnerability/CVE-2023-33979
Type: osv

## Details
gpt_academic provides a graphical interface for ChatGPT/GLM. A vulnerability was found in gpt_academic 3.37 and prior. This issue affects some unknown processing of the component Configuration File Handler. The manipulation of the argument file leads to information disclosure. Since no sensitive files are configured to be off-limits, sensitive information files in some working directories can be read through the `/file` route, leading to sensitive information leakage. This affects users that uses file configurations via `config.py`, `config_private.py`, `Dockerfile`. A patch is available at commit 1dcc2873d2168ad2d3d70afcb453ac1695fbdf02. As a workaround, one may use environment variables instead of `config*.py` files to configure this project, or use docker-compose installation to configure this project.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33979.json
- https://github.com/binary-husky/gpt_academic/security/advisories/GHSA-pg65-p24m-wf5g
- https://nvd.nist.gov/vuln/detail/CVE-2023-33979
- https://github.com/binary-husky/gpt_academic/commit/1dcc2873d2168ad2d3d70afcb453ac1695fbdf02
