# [M] Nezha Dashboard: DDNS and Notification credential exposure via unredacted list API

## Summary
Severity: Medium
Advisory: GHSA-ww5p-j6cj-6mqq
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-ww5p-j6cj-6mqq
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=0 <2.2.5

## Details
### Summary

The `GET /api/v1/ddns` and `GET /api/v1/notification` endpoints return full resource objects including plaintext third-party API credentials — Cloudflare API tokens, TencentCloud SecretKeys, Slack/Discord/Telegram webhook URLs with embedded bot tokens, and Authorization header values — without any field-level redaction. Any authenticated admin who calls these endpoints receives every stored credential in the system in a single API response. A compromised admin session or leaked PAT with `nezha:ddns:read` or `nezha:notification:read` scope exposes all third-party integration secrets.

### Details

The `listDDNS` and `listNotification` handlers follow an identical pattern: they call the corresponding singleton `GetSortedList()`, `copier.Copy` the full in-memory structs into a response slice, and return them via `listHandler` with zero field stripping.

**DDNS — `cmd/dashboard/controller/ddns.go:25–33`:**

```go
func listDDNS(c *gin.Context) ([]*model.DDNSProfile, error) {
    var ddnsProfiles []*model.DDNSProfile
    list := singleton.DDNSShared.GetSortedList()
    if err := copier.Copy(&ddnsProfiles, &list); err != nil {
        return nil, err
    }
    return ddnsProfiles, nil
}
```

The `DDNSProfile` struct (`model/ddns.go:20–36`) serializes `AccessSecret` with `json:"access_secret,omitempty"` — non-empty Cloudflare tokens and TencentCloud SecretKeys are returned in cleartext. The `WebhookURL` and `WebhookHeaders` fields may also contain embedded secrets.

**Notification — `cmd/dashboard/controller/notification.go:25–33`:**

```go
func listNotification(c *gin.Context) ([]*model.Notification, error) {
    slist := singleton.NotificationShared.GetSortedList()
    var notifications []*model.Notification
    if err := copier.Copy(&notifications, &slist); err != nil {
        return nil, err
    }
    return notifications, nil
}
```

The `Notification` struct (`model/notification.go:34–44`) serializes `URL`, `RequestHeader`, and `RequestBody` — all of which commonly contain embedded bot tokens (Slack, Discord, Telegram), API keys in Authorization headers, and webhook secrets.

**Route and authorization (`cmd/dashboard/controller/controller.go:155, 171`):**

```go
auth.GET("/notification", restScopeMiddleware(model.ScopeNotificationRead), listHandler(listNotification))
auth.GET("/ddns", restScopeMiddleware(model.ScopeDDNSRead), listHandler(listDDNS))
```

Both routes are behind `authMw` (JWT or PAT) and the corresponding read scope. The `listHandler` → `filter` chain uses `HasPermission` (`model/common.go:63–82`) which grants admins access to ALL profiles and restricts members to their own. No separate response struct or field masking exists anywhere in the codebase — confirmed by exhaustive search for `DDNSResponse`, `DDNSView`, `NotificationResponse`, `NotificationView`, or any JSON middleware that strips sensitive fields.

The codebase already demonstrates awareness of this pattern: `serverConfigSensitiveScope()` in `cmd/dashboard/controller/api_token_scope.go:117` was introduced to restrict `client_secret` exposure via `GET /server/config/:id`, tightening the scope from `ScopeServerRead` to `ScopeServerWrite`. No equivalent protection exists for the DDNS or Notification list endpoints.

**Tested at commit `3d74cd94` (master, post v2.2.3).** The vulnerable pattern has existed since the DDNS and notification list endpoints were introduced.

### PoC

1. Deploy nezha with at least one admin user. Configure a DDNS profile with a Cloudflare API token (AccessSecret) and a Notification webhook pointing to a Slack incoming webhook URL (`https://hooks.slack.com/services/T.../B.../xxx...`).

2. Authenticate as the admin user. Call:

   ```bash
   # DDNS credentials exposed
   curl -s -H "Authorization: Bearer <admin_jwt>" \
     https://dashboard.example.com/api/v1/ddns \
     | jq '.data[].access_secret'

   # Notification webhook secrets exposed
   curl -s -H "Authorization: Bearer <admin_jwt>" \
     https://dashboard.example.com/api/v1/notification \
     | jq '.data[].url'
   ```

3. Observe the full Cloudflare API token, Slack webhook URL with embedded token, and any `RequestHeader` values (e.g., `Authorization: Bearer ...`) returned in cleartext.

4. Alternatively, create a PAT with `nezha:ddns:read` scope:

   ```bash
   curl -s -H "Authorization: Bearer nzp_<pat_secret>" \
     https://dashboard.example.com/api/v1/ddns \
     | jq '.data[].access_secret'
   ```

   If the PAT creator is an admin, all DDNS secrets are returned in a single response.

5. **Negative control:** A member (non-admin) calling the same endpoints only sees their own profiles due to the `HasPermission` filter (`model/common.go:63–82`). However, an admin sees ALL profiles with ALL secrets. The security boundary crossed is the credential confidentiality boundary — a read-only listing endpoint should not return write-capable credentials.

### Impact

An attacker who compromises an admin session or obtains a PAT with the appropriate read scope can exfiltrate all third-party API credentials stored in the dashboard — Cloudflare API tokens, TencentCloud SecretKeys, Slack/Discord/Telegram bot tokens, and any secrets embedded in webhook URLs or Authorization headers. These credentials can then be used to:

- Modify DNS records for any domain managed via Cloudflare/TencentCloud DDNS profiles
- Send messages as the Slack/Discord/Telegram bot to any configured channel
- Access any other API the compromised credentials grant access to

The attack requires high privileges (admin JWT or PAT with appropriate scope), but the impact is amplified because a single API call exposes ALL stored credentials across ALL DDNS profiles and ALL notification webhooks, with no field-level access control separating metadata from secrets.

**Suggested remediation:** Introduce separate response structs (e.g., `DDNSProfileResponse`, `NotificationResponse`) that omit sensitive fields (`AccessSecret`, `WebhookHeaders`, `URL`, `RequestHeader`) from list/read endpoints, or use `json:"-"` tags on sensitive fields and provide them only through a dedicated credential-retrieval endpoint with stricter authorization (analogous to the existing `serverConfigSensitiveScope()` pattern).

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-ww5p-j6cj-6mqq
- https://github.com/nezhahq/nezha
