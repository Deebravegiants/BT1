# [H] Flowise: Password Reset Link Sent Over Unsecured HTTP

## Summary
Severity: High
Advisory: GHSA-x5w6-38gp-mrqh
CVE: CVE-2026-41275
CWE: CWE-319
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-x5w6-38gp-mrqh
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
**Summary:**
The password reset functionality on [cloud.flowiseai.com](http://cloud.flowiseai.com/) sends a reset password link over the unsecured HTTP protocol instead of HTTPS. This behavior introduces the risk of a man-in-the-middle (MITM) attack, where an attacker on the same network as the user (e.g., public Wi-Fi) can intercept the reset link and gain unauthorized access to the victim’s account.

**Steps to Reproduce:**
1. Sign up for a new account on https://cloud.flowiseai.com/register.
2. Navigate to the https://cloud.flowiseai.com/forgot-password page and enter your email.
3. Open your inbox and locate the password reset email.
4. Copy the reset link and inspect its protocol – it uses http:// instead of https://.

**POC:**
http://[url6444.mail.flowiseai.com/ls/click?upn=u001.wa3d8yQsDRACvrFO3KPOeg4btvV98-2FRrNXRtYO9s9CtK622C9ChG4-2BvVg73Tvckl-2B5NZdaQcY4lfu7-2FJ5x9CldlKHZK4mop-2Bv-2FhMDPBX-2FtRDjG7vM-2FSMz1nPIQL3FS94nJSjGnZOW38kMxxMCP92yr092lV1KNGMVDr8xaCpM3k-3D1zEv_0Wzb2YTtJ6lxixf7gbrDfWWVoz-2B4mHPzoyxr9IPI-2Fas8GiBp1THEcPQTeIcCYlgaV0UaD8Y2wiA4ZRRCAp-2BjS0SMkthmibNAiBs2GZjXIaV-2F2wTIaJJdFXWkhTB-2Fc8hJjDhpLnRfayLJ5HyG9gftPNPM-2F9t9DvyHB-2FYLpZzAvou6jB8Nr-2BBFjyWBFrNq0g6su6i-2BwFySXSA-2Bzyg94PQKOA-3D-3D](http://url6444.mail.flowiseai.com/ls/click?upn=u001.wa3d8yQsDRACvrFO3KPOeg4btvV98-2FRrNXRtYO9s9CtK622C9ChG4-2BvVg73Tvckl-2B5NZdaQcY4lfu7-2FJ5x9CldlKHZK4mop-2Bv-2FhMDPBX-2FtRDjG7vM-2FSMz1nPIQL3FS94nJSjGnZOW38kMxxMCP92yr092lV1KNGMVDr8xaCpM3k-3D1zEv_0Wzb2YTtJ6lxixf7gbrDfWWVoz-2B4mHPzoyxr9IPI-2Fas8GiBp1THEcPQTeIcCYlgaV0UaD8Y2wiA4ZRRCAp-2BjS0SMkthmibNAiBs2GZjXIaV-2F2wTIaJJdFXWkhTB-2Fc8hJjDhpLnRfayLJ5HyG9gftPNPM-2F9t9DvyHB-2FYLpZzAvou6jB8Nr-2BBFjyWBFrNq0g6su6i-2BwFySXSA-2Bzyg94PQKOA-3D-3D)

**Impact:**
If a victim receives this insecure link and uses it over an untrusted network, an attacker can sniff the traffic and capture the reset token. This allows the attacker to hijack the victim's password reset session, potentially compromising their account.

**Mitigation:**
Ensure all sensitive URLs, especially password reset links, are generated and transmitted over secure https:// endpoints only.

**Best Practice:**
Use HTTPS in all password-related email links.
Implement HSTS (HTTP Strict Transport Security) to enforce secure connections.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x5w6-38gp-mrqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41275
- https://hackerone.com/reports/1888915
- https://github.com/FlowiseAI/Flowise
