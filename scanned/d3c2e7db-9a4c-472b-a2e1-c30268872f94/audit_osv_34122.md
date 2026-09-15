# [C] Zed AI Agent Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-55012
Aliases: GHSA-x34m-39xw-g2wr
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-55012
Type: osv

## Details
Zed is a multiplayer code editor. Prior to version 0.197.3, in the Zed Agent Panel allowed for an AI agent to achieve Remote Code Execution (RCE) by bypassing user permission checks. An AI Agent could have exploited a permissions bypass vulnerability to create or modify a project-specific configuration file, leading to the execution of arbitrary commands on a victim's machine without the explicit approval that would otherwise be required. This vulnerability has been patched in version 0.197.3. A workaround for this issue involves either avoid sending prompts to the Agent Panel, or to limit the AI Agent's file system access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55012.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-x34m-39xw-g2wr
- https://nvd.nist.gov/vuln/detail/CVE-2025-55012
