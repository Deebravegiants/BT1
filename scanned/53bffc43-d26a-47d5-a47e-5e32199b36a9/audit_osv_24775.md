# [H] Command Injection in Cocos Engine workflow

## Summary
Severity: High
Advisory: CVE-2023-26493
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-26493
Type: osv

## Details
Cocos Engine is an open-source framework for building 2D & 3D real-time rendering and interactive content. In the github repo for Cocos Engine the `web-interface-check.yml` was subject to command injection. The `web-interface-check.yml` was triggered when a pull request was opened or updated and contained the user controllable field `(${{ github.head_ref }} – the name of the fork’s branch)`. This would allow an attacker to take over the GitHub Runner and run custom commands (potentially stealing secrets such as GITHUB_TOKEN) and altering the repository. The workflow has since been removed for the repository. There are no actions required of users.

## References
- https://github.com/cocos/cocos-engine/blob/2362df28a4b3016dbda804899041279701929728/.github/workflows/web-interface-check.yml
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26493.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26493
- https://securitylab.github.com/advisories/GHSL-2023-027_Engine_for_Cocos_Creator/
- https://github.com/cocos/cocos-engine/commit/6d06aefa2684e20da79e7ceaf41f728c1a8d7a41
