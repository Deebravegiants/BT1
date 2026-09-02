Confirmed: `WebhookMetadata.shop` (used by every downstream `WebhookHandler#handle` implementation as the tenant identifier) is populated straight from the unauthenticated `shop-domain` header, while `Utils::HmacValidator.validate` only verifies the raw body via `Request#to_signable_string`, which returns `@raw_body` alone.### Title
Cross-tenant webhook spoofing via `shop-domain` header not covered by HMAC verification - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, then hands the caller-supplied `shop-domain` header straight to the app's `WebhookHandler#handle` as the trusted tenant identifier. The HMAC never covers this header, so the "shop the request is verified for" and "the shop attributed to the payload" are two different, unbound values.

### Finding Description
`Registry.process` gates all webhook processing on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body — nothing else: [3](#0-2) 

Meanwhile `Request#shop` is read verbatim from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed material at all: [4](#0-3) [5](#0-4) 

That unauthenticated value is then passed as the `shop` field of `WebhookMetadata`, the struct every registered `WebhookHandler#handle` implementation receives and is expected to treat as the tenant/store the event belongs to: [6](#0-5) [7](#0-6) 

The broken equality is: `shop authenticated by HMAC (none — body only)` ≠ `shop used as the tenant key by the handler (request.shop, header-derived)`.

Because the same `api_secret_key` is shared across every shop installed on a given app, any party who legitimately receives one correctly signed webhook body+HMAC pair for **their own** shop (any merchant that installs the app can trivially obtain this, since Shopify delivers real signed webhooks to their configured endpoint/logs) can replay that identical body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header for an arbitrary victim shop. `HmacValidator.validate` will still succeed, because it only checks the body against the shared secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originates from the victim shop.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (the field this gem explicitly exposes and documents as the webhook's shop) to route data, update per-tenant state, or look up a session for that store — which is the documented purpose of the field — an attacker can inject arbitrary-looking webhook events attributed to a shop they do not own. This is a cross-tenant data-integrity/confusion issue: the gem's own signature verification cannot distinguish "this body is authentic for shop A" from "this body is authentic but relabeled as shop B," because shop identity is never part of what is cryptographically verified.

### Likelihood Explanation
Any entity that can install the target app on at least one shop (a normal, low-privilege action available to any Shopify merchant/developer) automatically receives legitimately HMAC-signed webhook deliveries for that shop. Replaying the body/HMAC with a modified `shop-domain` header requires only a basic HTTP client — no secret key, token, or elevated access is needed beyond having one's own shop install the app. This makes the analog realistically reachable by an unprivileged internet-adjacent actor.

### Recommendation
Bind the shop identity into the value that is actually authenticated. At minimum:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header in the signable string used by `Request#to_signable_string`, so the HMAC computed in `HmacValidator.compute_signature` covers shop identity, not just the body, or
- Have `Registry.process` cross-check `request.shop` against an independently-verified source (e.g., the shop tied to the session/webhook subscription used to register the handler) before constructing `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the delivered raw body and `x-shopify-hmac-sha256` header (both are legitimate and pass verification).
2. Replay the exact same raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the unchanged body against the shared `api_secret_key`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:198-199`) invokes the app's `WebhookHandler#handle` with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the payload never touched that shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
