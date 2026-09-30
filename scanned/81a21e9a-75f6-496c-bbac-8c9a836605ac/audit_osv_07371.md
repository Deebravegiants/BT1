# [M] Windows Defender Application Control Security Feature Bypass Vulnerability

## Summary
Severity: Medium
Advisory: BIT-powershell-2020-0951
Aliases: CVE-2020-0951
Ecosystem: Bitnami
Published: 2025-09-04
Source: https://osv.dev/vulnerability/BIT-powershell-2020-0951
Type: osv

## Affected
- Bitnami: `powershell` — affected >=7.1.0 <7.1.5, >=7.0.8

## Details
<p>A security feature bypass vulnerability exists in Windows Defender Application Control (WDAC) which could allow an attacker to bypass WDAC enforcement. An attacker who successfully exploited this vulnerability could execute PowerShell commands that would be blocked by WDAC.</p>
<p>To exploit the vulnerability, an attacker need administrator access on a local machine where PowerShell is running. The attacker could then connect to a PowerShell session and send commands to execute arbitrary code.</p>
<p>The update addresses the vulnerability by correcting how PowerShell commands are validated when WDAC protection is enabled.</p>

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0951
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0951
