# [H] Wazuh NetNTLMv2 Hash Theft In Multiple Centralized Configuration Capabilities

## Summary
Severity: High
Advisory: CVE-2025-30201
Aliases: GHSA-x697-jf34-gp5x
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-30201
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Prior to version 4.13.0, a vulnerability in Wazuh Agent allows authenticated attackers to force NTLM authentication through malicious UNC paths in various agent configuration settings, potentially leading NTLM relay attacks that would result privilege escalation and remote code execution. This issue has been patched in version 4.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30201.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-x697-jf34-gp5x
- https://nvd.nist.gov/vuln/detail/CVE-2025-30201
- https://github.com/wazuh/wazuh/commit/688972da589e5d40d2a81bcd738240303a3dc45a
- https://github.com/wazuh/wazuh/pull/30060
