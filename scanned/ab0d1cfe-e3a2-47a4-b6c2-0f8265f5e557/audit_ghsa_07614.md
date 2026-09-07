# [H] Gogs Vulnerable to  2FA Bypass via Recovery Code

## Summary
Severity: High
Advisory: GHSA-p6x6-9mx6-26wj
CVE: CVE-2025-64175
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-p6x6-9mx6-26wj
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0.11.19 <0.13.4

## Details
Contact OpenAI Security Research at outbounddisclosures@openai.com to engage on this report.  
See PDF report for easier reading.

Security Advisory: 2FA Bypass via Recovery Code
Vulnerability Type: 2FA Authentication Bypass
Affected Software: GOGS
Severity: High
Date: Aug 5, 2025
Discoverer: OpenAI Security Research
Summary
Gogs’ 2FA recovery code validation does not scope codes by user, enabling cross-account bypass. If an attacker knows a victim’s username and password, they can use
[Security Advisory_ 2FA Bypass via Recovery Code - Google Docs.pdf](https://github.com/user-attachments/files/21643266/Security.Advisory_.2FA.Bypass.via.Recovery.Code.-.Google.Docs.pdf)
 any unused recovery code (e.g., from their own account) to bypass the victim’s 2FA. This enables full account takeover and renders 2FA ineffective in all environments where it's enabled.
Affected Versions
Software: [Gogs](https://github.com/gogs/gogs/tree/main)
Confirmed Version(s): All versions with 2FA support
Likely Affected: All versions since introduction of UseRecoveryCode logic
Introduced Commit: [a617d52374e937db0edacfba2a26bdd14a05538e](https://github.com/gogs/gogs/commit/a617d52374e937db0edacfba2a26bdd14a05538e) 
Commit: a617d52374e937db0edacfba2a26bdd14a05538e
Author: Joe Chen
Date: Apr 5, 2017
Description: 2fa: initial support 

Vulnerability Details
The function UseRecoveryCode in internal/database/two_factor.go fails to check that the recovery code belongs to the authenticating user. Instead, it looks for any unused recovery code:
Vulnerable Code Snippet
```go
func UseRecoveryCode(_ int64, code string) error {
    recoveryCode := new(TwoFactorRecoveryCode)
    has, err := x.Where("code = ?", code).And("is_used = ?", false).Get(recoveryCode)
    ...
}
```
Although the caller passes userID, it is ignored. The result is a global lookup for any unused code, allowing an attacker to submit their own recovery code during another user's login flow.

Call Chain

web login handler
  → UseRecoveryCode(userID, code)
    → DB query without userID constraint
Proof-of-Concept (PoC)
Description
This bug is tested against the latest version of Gogs hosted on [Dockerhub](https://hub.docker.com/r/gogs/gogs). Attacker uses their own recovery code to bypass another user’s 2FA.
Steps
Create attacker account A and enable 2FA. Save a code like "abcde-fghij".
Obtain credentials for victim B.
Attempt login as B via web.
When prompted for recovery code, submit A's code.
Login as B succeeds; A's code is marked as used.


Impact
2FA rendered ineffective for all users
Realistic Exploitation Scenarios
Public Gogs instances with 2FA enabled
Developer or maintainer accounts
Enterprise self-hosted Gogs servers
Potential Impact
This vulnerability critically undermines 2FA. Since recovery codes are not globally unique and lack user scoping, any attacker with victim credentials can use one of their own recovery codes to complete login as the victim — bypassing all 2FA protections. This opens the door to account hijacking, data exfiltration, and downstream supply chain compromise.
Timeline
August 2025: Discovered via GPT5
August 2025: Reproduced and confirmed via PoC and sanitizer
Aug 6, 2025 - Sent to Gogs via https://github.com/gogs/gogs/security/advisories/new


This information is being shared by OpenAI solely for the purpose of improving security and reducing potential harm. This information is presented as-is.  OpenAI Security Research makes no representations or warranties, express or implied, as to the completeness, accuracy, or fitness for any particular purpose of the information. [This includes, without limitation any suggestions or ideas presented on how to remedy or mitigate an identified vulnerability, including whether such suggestions or ideas would be effective and/or could have other negative impacts.]
OpenAI disclaims any liability for direct or indirect damages arising from the reliance on, or use, misuse, or interpretation of this information. Any references to third-party systems, services, or entities are included solely for identification purposes and do not imply endorsement, responsibility, or attribution.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-p6x6-9mx6-26wj
- https://nvd.nist.gov/vuln/detail/CVE-2025-64175
- https://github.com/gogs/gogs/commit/a617d52374e937db0edacfba2a26bdd14a05538e
- https://github.com/gogs/gogs/commit/d568e048315dc9729c8518d8085cab7dbbfac80f
- https://github.com/gogs/gogs
