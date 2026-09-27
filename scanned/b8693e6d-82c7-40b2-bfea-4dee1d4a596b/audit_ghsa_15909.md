# [H] Gradio has a race condition in update_root_in_config may redirect user traffic

## Summary
Severity: High
Advisory: GHSA-xh2x-3mrm-fwqm
CVE: CVE-2024-47870
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-xh2x-3mrm-fwqm
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact  
**What kind of vulnerability is it? Who is impacted?**

This vulnerability involves a **race condition** in the `update_root_in_config` function, allowing an attacker to modify the `root` URL used by the Gradio frontend to communicate with the backend. By exploiting this flaw, an attacker can redirect user traffic to a malicious server. This could lead to the interception of sensitive data such as authentication credentials or uploaded files. This impacts all users who connect to a Gradio server, especially those exposed to the internet, where malicious actors could exploit this race condition.

### Patches  
Yes, please upgrade to `gradio>=5` to address this issue.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-xh2x-3mrm-fwqm
- https://nvd.nist.gov/vuln/detail/CVE-2024-47870
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-218.yaml
