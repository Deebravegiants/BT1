# [M] Decidim: Push subscriptions can be abused for server-side requests

## Summary
Severity: Medium
Advisory: GHSA-2g9c-vf8h-prxx
CVE: CVE-2026-45573
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-2g9c-vf8h-prxx
Type: github-advisory

## Affected
- RubyGems: `decidim-core` — affected >=0 <0.30.9
- RubyGems: `decidim-core` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-core` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description

The push-subscription endpoint stores an attacker-controlled delivery URL, and the notification send path becomes an outbound-request sink when VAPID delivery is enabled. The practical result is an authenticated, stored, mostly blind SSRF primitive to arbitrary HTTPS endpoints reachable from the app server.

## Technical description
 
When VAPID delivery is enabled, the notification subscription flow stores the client-supplied push endpoint without checking that it belongs to an approved push service. The send path later passes that stored URL to `WebPush.payload_send`, turning the subscription into an attacker-controlled outbound request destination.
This is the source-to-sink chain:

1. Source: attacker-controlled `subscription.endpoint` in the JSON body posted to `POST /notifications_subscriptions`.
2. Persistence: `params[:endpoint]` is stored under `user.notification_settings["subscriptions"]`.
3. Retrieval: `user.notifications_subscriptions.values` returns that stored endpoint later.
4. Sink: `build_payload` sets `endpoint: subscription["endpoint"]`.
5. Outbound request: `WebPush.payload_send(**payload)` uses the attacker-supplied endpoint as the
destination.

One spec asserts that the endpoint is persisted exactly as supplied:

```ruby
# decidim-core/spec/services/decidim/notifications_subscriptions_persistor_spec.rb
expect(user.notifications_subscriptions["auth_code_121"]["endpoint"]).to eq(params[:endpoint])
```

Another spec asserts that `SendPushNotification` passes the stored endpoint into `WebPush.payload_send`:

```ruby
# decidim-core/spec/services/decidim/send_push_notification_spec.rb
first_notification_payload = {
  message:,
  endpoint: subscriptions["auth_key_1"]["endpoint"],
  p256dh: subscriptions["auth_key_1"]["p256dh"],
  auth: subscriptions["auth_key_1"]["auth"],
  vapid: a_hash_including(...)
}
expect(WebPush).to receive(:payload_send).with(first_notification_payload)
```

### Impact

- In a configured deployment, an authenticated user can register an attacker-controlled or otherwise unauthorized HTTPS URL.
- The server then sends outbound `POST` requests there whenever a notification is pushed.
- This is a stored, mostly blind SSRF primitive: useful for outbound interaction with attacker infrastructure and, where routable, internal HTTPS services.
- Notification metadata is disclosed to the supplied endpoint through the encrypted web push request path.

### Patches

See https://github.com/decidim/decidim/pull/16714.

### Workarounds

Disable the push notifications feature by removing the VAPID keys in the server.

### Resource

SSRF

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-2g9c-vf8h-prxx
- https://github.com/decidim/decidim/pull/16714
- https://github.com/decidim/decidim
