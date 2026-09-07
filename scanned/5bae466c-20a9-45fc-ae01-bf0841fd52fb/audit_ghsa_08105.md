# [C] Known affected by Account Takeover via Password Reset Token Leakage

## Summary
Severity: Critical
Advisory: GHSA-78wq-6gcv-w28r
CVE: CVE-2026-26273
CWE: CWE-200, CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-78wq-6gcv-w28r
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0 <1.6.3

## Details
### Summary
A Critical Broken Authentication vulnerability exists in Known 1.6.2. The application leaks the password reset token within a hidden HTML input field on the password reset page. This allows any unauthenticated attacker to retrieve the reset token for any user by simply querying the user's email, leading to full Account Takeover (ATO) without requiring access to the victim's email inbox.

### Details
The vulnerability occurs within the password reset flow. When a reset is requested, the application generates a verification code. However, the subsequent reset page (/account/password/reset/) incorrectly reflects this code back to the client in the HTML source code.

Specifically, the sensitive token is embedded in:
<input type="hidden" name="code" value="[SECRET_TOKEN]">

Because this page is accessible via a GET request using the victim's email as a parameter, an attacker can programmatically extract the token.

### PoC
1. The attacker asks for a password reset for the victim

<img width="1328" height="580" alt="image" src="https://github.com/user-attachments/assets/0197907e-f10b-4e6d-989e-f25c408862cd" />

<img width="1139" height="452" alt="image(1)" src="https://github.com/user-attachments/assets/9a317b27-b56a-4663-9965-d3e660713f4e" />


2. The attacker makes the following curl command on the terminal using the victim's email, and is able to get the code that was sent as an hidden field in the HTML.
<img width="917" height="220" alt="image(2)" src="https://github.com/user-attachments/assets/af89ba3b-de56-4437-84b3-c1feb56d2348" />

3. With this code, the attacker is able to use it in order to reset the victim password.
<img width="1335" height="711" alt="image(3)" src="https://github.com/user-attachments/assets/498b8a2e-9eb2-4b50-bc35-26b0f2764c8d" />

<img width="1258" height="524" alt="image(4)" src="https://github.com/user-attachments/assets/d1304dc3-bf56-4ec7-920c-ecce502db6b0" />

4. The attacker is able to login with the new password.

<img width="1514" height="631" alt="image(5)" src="https://github.com/user-attachments/assets/2533032e-6f0d-45c8-9fe1-881bfedebcc4" />

<img width="1528" height="647" alt="image(6)" src="https://github.com/user-attachments/assets/a6e9144c-cc96-493d-8780-9156c299a192" />



### Impact
- An attacker can compromise any account on the platform, including administrative accounts, resulting in total loss of Confidentiality, Integrity, and Availability.

## References
- https://github.com/idno/known/security/advisories/GHSA-78wq-6gcv-w28r
- https://github.com/idno/known/commit/8439a0747471559fb1ea9f074b929d390f27e66a
- https://github.com/idno/known
- https://github.com/idno/known/releases/tag/1.6.3
