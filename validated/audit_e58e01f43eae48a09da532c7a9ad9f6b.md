### Title
Webhook shop domain and topic are trusted from unauthenticated headers while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the webhook HMAC only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are read directly from HTTP headers that are never covered by that HMAC. Since the app's `api_secret_key` used for webhook HMAC signing is shared across every shop that installs the app (it is not per-shop), any merchant who legitimately installs the app can obtain a genuinely HMAC-valid `(body, hmac)` pair from their own store's webhooks and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` header, causing the app to process the payload as if it originated from a different shop or a different event type.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as the raw request body only: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate, unauthenticated HTTP headers: [3](#0-2) 

`Registry.process` uses these unauthenticated header-derived values to both dispatch to a handler (keyed by `request.topic`) and to construct the `WebhookMetadata` passed to the handler, which includes `request.shop`: [4](#0-3) 

The HMAC only proves "this body byte sequence was signed with `api_secret_key`" — it says nothing about which shop or topic the body is being claimed for. Because `api_secret_key` is a single shared secret for the whole app (not scoped per shop), any shop that installs the app receives genuinely-signed webhooks from Shopify and can capture a valid `(raw_body, hmac)` pair. That pair remains cryptographically valid no matter what `shop-domain`/`topic`/`webhook-id`/`api-version` headers are sent alongside it, because those fields are never part of the signed bytes.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: `hmac verifies bytes(body)` but the code equates `identity(shop, topic) == headers`, when the equality that should hold is `identity(shop, topic) == HMAC-authenticated(shop, topic)`.

### Impact Explanation
An attacker who legitimately installs the target app on their own store (a routine, unprivileged action for any Shopify developer/merchant) can:
1. Capture a genuine webhook `(raw_body, x-shopify-hmac-sha256)` pair sent to their own endpoint (e.g. via a proxy/logging tool).
2. Replay that exact body and HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` for a victim shop and/or `X-Shopify-Topic` for a different registered topic.
3. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is legitimate), so `Registry.process` dispatches the handler and hands it a `WebhookMetadata` claiming to be from the victim shop and/or a different event.

Depending on how the host app's webhook handlers act on `WebhookMetadata#shop` (e.g. revoking/rotating a session, processing `app/uninstalled`, `customers/redact`, `shop/update`, or other privileged per-shop side effects), this enables cross-tenant confusion/attribution: actions intended for one merchant can be triggered and attributed to another merchant's shop, without the attacker ever possessing that shop's credentials. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any threat actor can install a Shopify app for free (development stores are freely creatable) and thus always has a supply of validly-signed webhook bodies for their own shop. Replaying an HTTP POST with modified headers requires no special access, no leaked secrets, and no privileged account — it is achievable by any unprivileged internet user who can install the target app once. The likelihood is High.

### Recommendation
Bind the routing/attribution fields into the HMAC-verified payload instead of trusting separate headers:
- Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable bytes (or otherwise cryptographically bind them), or
- Independently verify that the `shop` header corresponds to a shop with a currently valid, stored session/access token for this app before processing the webhook, and reject webhooks whose claimed topic wasn't the one actually registered for the delivery, and
- Document this expectation clearly for `ShopifyAPI::Webhooks::Registry.process` consumers so host apps don't rely solely on `HmacValidator.validate` for shop/topic authenticity.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and captures a real webhook delivery, e.g. "orders/create":
raw_body = '{"id": 123, "note": "hello"}'
hmac      = "<value Shopify actually computed with the shared api_secret_key>"

# Attacker replays it to the app's public webhook endpoint, forging headers:
headers = {
  "x-shopify-topic"       => "customers/redact",       # different topic than originally signed for
  "x-shopify-hmac-sha256" => hmac,                      # still valid: HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not attacker's own shop
  "x-shopify-webhook-id"  => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac match),
#    handler for "customers/redact" is invoked with shop: "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
