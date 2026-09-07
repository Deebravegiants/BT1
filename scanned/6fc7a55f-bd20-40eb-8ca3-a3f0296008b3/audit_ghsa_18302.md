# [C] DNN Vulnerable to Stored Cross-Site Scripting (XSS) in the Prompt module

## Summary
Severity: Critical
Advisory: GHSA-2qxc-mf4x-wr29
CVE: CVE-2025-59545
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-2qxc-mf4x-wr29
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <10.1.0

## Details
# Summary
The Prompt module allows execution of commands that can return raw HTML. Malicious input, even if sanitized for display elsewhere, can be executed when processed through certain commands, leading to potential script execution (XSS).

# Description
The application sanitizes most user-submitted data before displaying it in entry forms. However, the Prompt module is capable of running commands whose output is treated as HTML. This creates a vulnerability where a malicious user can craft input containing embedded scripts or harmful markup.

If such malicious content is later processed by a Prompt command and returned as HTML, it bypasses the standard sanitation mechanisms. Simply executing a specific command through the Prompt module could render this untrusted data and cause unintended script execution in the browser specially in the context of a super-user.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-2qxc-mf4x-wr29
- https://nvd.nist.gov/vuln/detail/CVE-2025-59545
- https://github.com/dnnsoftware/Dnn.Platform
