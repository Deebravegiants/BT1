### Title
Webhook processing binds `shop`/`topic`/`webhook_id` from unauthenticated HTTP headers while the HMAC signature only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop`, `topic`, and `webhook_id` values that are subsequently trusted and handed to the app's business logic are read straight from HTTP headers that are **not** part of the signed message. Anyone who possesses one valid `(raw_body, hmac)` pair — which they can obtain legitimately for their own shop, since Shopify signs webhooks with the app's shared `client_secret` for every installed shop — can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` (and topic/webhook-id) header. The signature will still validate because those fields never entered `to_signable_string`, so the handler will process the payload as if it originated from a shop the attacker doesn't own.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the supplied `hmac`. For webhooks, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id`, however, are read from separate HTTP headers that are never fed into the signature: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then dispatches the handler using the unauthenticated header-derived `shop`/`topic`/`webhook_id`: [3](#0-2) 

This breaks the identity binding: `shop_verified_by_hmac (∅, not covered)` ≠ `shop_used_by_handler (Request#shop header value)`. The signature proves "this exact body byte-string was signed with the app's secret at some point, for some shop," but not "this body came from shop X." Because Shopify signs webhooks per-installation using the same app-level `client_secret` for every merchant that installs the app, any merchant (an ordinary, unprivileged installer of the app — no special privilege required) can:
1. Install the target app on their own store and receive a legitimately signed webhook (`raw_body`, valid `hmac`, headers including their own `shop-domain`).
2. Replay that exact `raw_body`/`hmac` pair directly to the app's public webhook endpoint, overriding only the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a victim shop.
3. `Utils::HmacValidator.validate` still returns `true` (body unchanged), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: <victim-shop>, ...)`, so the app performs shop-scoped side effects (e.g. uninstall cleanup, GDPR erasure, entitlement changes) against the victim tenant using attacker-supplied timing/body content.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who legitimately controls only their own shop can make the app believe a webhook event (e.g. `app/uninstalled`, `shop/update`, `customers/redact`) came from a different, unrelated shop, and the app's webhook handler will act on that victim shop's data/session state. This matches the Critical "cross-tenant access" impact category, since the tenant boundary (`shop`) that the rest of the library and downstream app logic rely on for authorization is not actually bound by the cryptographic check that is supposed to authenticate the request.

### Likelihood Explanation
No privileged credentials, leaked secrets, or TLS interception are required. Any user can install the target app on their own store for free/trial, capture one legitimate webhook delivery, and immediately replay it with a modified `shop-domain` header to the app's public webhook URL. The only requirement is that the app registered at least one webhook and exposes the endpoint publicly, which is standard practice for every embedded Shopify app using this library's `Webhooks::Registry`.

### Recommendation
Bind the identity fields into the signed material, or otherwise cross-check them against an independent trusted source before dispatch:
- Include `shop`, `topic`, and `webhook_id` (not just the raw body) in `to_signable_string` for `Webhooks::Request`, if Shopify's webhook signing scheme supports it, or
- Require the consuming application to verify that the `shop` on the webhook belongs to a shop with an active, previously-stored session/installation before invoking the handler, rather than trusting the header value outright, and
- Document explicitly (and enforce at the library level, if feasible) that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated header values and must be independently validated against stored installation records prior to acting on them.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app,
# so Shopify sends them a legitimately HMAC-signed webhook:
raw_body = '{"id":123,"note":"hello"}'
hmac     = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)
# (attacker doesn't know APP_CLIENT_SECRET, but Shopify computed this hmac for them
#  and delivered it to the attacker's own webhook receiver)

# Attacker now replays the exact same (raw_body, hmac) pair to the app's endpoint,
# but swaps the shop-domain header to a victim shop:
forged_headers = {
  "shopify-topic"       => "app/uninstalled",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # <-- not covered by HMAC
  "shopify-webhook-id"  => "attacker-controlled-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (only raw_body is checked), and the handler is invoked
#    with shop == "victim-shop.myshopify.com", even though that shop never sent this event.
``` [4](#0-3)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
