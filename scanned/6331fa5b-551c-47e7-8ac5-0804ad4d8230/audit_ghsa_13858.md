# [M] Update share links to use FRP instead of SSH tunneling

## Summary
Severity: Medium
Advisory: GHSA-3x5j-9vwr-8rr5
CVE: CVE-2023-25823
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-3x5j-9vwr-8rr5
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <3.13.1

## Details
### Impact
This is a vulnerability which affects anyone using Gradio's share links (i.e. creating a Gradio app and then setting `share=True`) with Gradio versions older than 3.13.1. In these older versions of Gradio, a private SSH key is sent to any user that connects to the Gradio machine, which means that a user could access other users' shared Gradio demos. From there, other exploits are possible depending on the level of access/exposure the Gradio app provides. 

### Patches
The problem has been patched. Ideally, users should upgrade to `gradio==3.19.1` or later where the FRP solution has been properly tested. 

### Credit
Credit to Greg Sadetsky and Samuel Tremblay-Cossette for alerting the team

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-3x5j-9vwr-8rr5
- https://nvd.nist.gov/vuln/detail/CVE-2023-25823
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2023-16.yaml
