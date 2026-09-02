### Title
Webhook HMAC covers only the raw body, not the `shop-domain` header — enables cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` never covers the `shop-domain` (or `topic`/`webhook-id`/`api-version`) header. `Registry.process` nonetheless trusts `request.shop` — taken straight from that unauthenticated header — and hands it to the webhook handler as the tenant identifier. Any party who can obtain one genuine, validly-signed webhook body for *any* shop (e.g., their own installed app instance) can replay that same body/HMAC pair while swapping the `shop-domain` header to a victim shop, and the library will report it as an authentic webhook "from" the victim.

### Finding Description
The library's webhook signature check is: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, and `HmacValidator.validate_signature`/`compute_signature` sign nothing but this string: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the body's signature: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler — the very value used by host applications to select which tenant's session/data to act on: [4](#0-3) 

Because every shop installed under a given app shares the same `api_secret_key` (`Context.api_secret_key` is a single, app-wide secret, not per-shop), the HMAC over the body is valid for *any* shop that uses this app — it's a property of the app, not the tenant. This breaks the intended binding:

`shop header used to route/act on webhook data == shop actually authenticated by the HMAC`

Before the attacker's request: for a genuine webhook, `shop-domain` header equals the shop whose data produced the body, and that pairing is implicitly correct because Shopify itself sends both.
After the attacker's request: the attacker (who owns a legitimate, unprivileged install of the app on their own shop) captures one legitimate `(raw_body, hmac)` pair for their own shop, then re-sends it to the app's webhook endpoint with `shopify-shop-domain` swapped to a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the (unchanged) body against the shared secret; `request.shop` now equals the victim shop, so `Registry.process` calls the handler with `WebhookMetadata.new(... shop: <victim>, body: <attacker's own body> ...)`.

### Impact Explanation
This is a cross-tenant integrity/confidentiality violation: a webhook payload can be attributed to an arbitrary victim shop while being fully "valid" per this gem's own verification (`Utils::HmacValidator.validate` returns true). Any host application that uses `WebhookMetadata#shop` to select the tenant session, update tenant records, trigger tenant-scoped side effects (inventory sync, order processing, uninstall/GDPR flows, etc.) can be made to act on forged or mismatched data under another merchant's identity — a cross-tenant access condition, which the rules classify as Critical impact.

### Likelihood Explanation
Likelihood is low-to-moderate: the attacker must control (or observe) one legitimate app installation to obtain a validly-signed webhook body — trivially available to anyone who installs the app on their own store, which is normal, unprivileged "internet user" access to a public app. No access token, `client_secret`, or TLS interception is required; only network access to the app's public webhook endpoint and one prior valid webhook delivery to their own shop.

### Recommendation
Include the tenant-identifying header(s) in the signed/verified material, or otherwise cryptographically or contextually bind `shop-domain` to the payload before trusting it:
- At minimum, extend `to_signable_string` (or add a separate check in `Registry.process`) to ensure the `shop-domain` header matches an expected/whitelisted shop for the given webhook context, and document that host apps must independently verify `WebhookMetadata#shop` against their own installed-shop registry rather than trusting it implicitly.
- Alternatively/additionally, warn/require host applications to cross-check `request.shop` against a shop this app instance is actually installed on (e.g. via session store) prior to acting on the payload.

### Proof of Concept
```ruby
# Attacker owns/installs the app on their own shop "attacker-shop.myshopify.com"
# and receives a genuine webhook (raw_body, hmac) pair for it, e.g. via app logs / their own server.

raw_body = '{"id":123,"note":"hi"}'
valid_hmac_b64 = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), Context.api_secret_key, raw_body)
)

# Attacker resends the identical body+hmac to the app's public webhook endpoint,
# only changing the shop-domain header to a victim shop they do NOT control.
forged_headers = {
  "x-shopify-topic"        => "orders/updated",
  "x-shopify-hmac-sha256"  => valid_hmac_b64,
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/HMAC match),
#    handler is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker-controlled body)
``` [5](#0-4) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
