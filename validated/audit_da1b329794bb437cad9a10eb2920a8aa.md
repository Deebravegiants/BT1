Confirmed. This is sufficient to finalize the analysis.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted for tenant routing without HMAC coverage - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from only the raw request body, while the shop identity, topic, and webhook id used to route the webhook to a tenant-specific handler are taken from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC solely over that signable string using the app-level `Context.api_secret_key` [2](#0-1) . However, `Request#shop`, `#topic`, and `#webhook_id` are all read directly from HTTP headers with no cryptographic binding to the body or its HMAC [3](#0-2) . `Registry.process` validates only the HMAC of the request and then immediately builds `WebhookMetadata` — including `shop` — straight from these unauthenticated headers, passing it to the host app's handler as the tenant identity [4](#0-3) . The `WebhookMetadata` struct treats `shop` as a plain trusted field consumed by `WebhookHandler#handle` [5](#0-4) .

Because `Context.api_secret_key` is a single **app-level** secret shared across every shop that installs the app (not a per-shop secret), any user who installs the app on their own store legitimately receives real webhook deliveries with valid `(body, hmac)` pairs. Since the HMAC signable string is body-only, that same `(body, hmac)` pair remains valid no matter what `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` header values are attached to the replayed request. This breaks the intended binding: `shop header used for tenant routing == shop authenticated by the HMAC`. In truth, HMAC verification proves only "this body was HMAC'd with this app's secret" — not "this body belongs to shop X" or "this topic is Y."

### Impact Explanation
An attacker who is merely an unprivileged installer of the target app on their own (attacker-controlled) shop can capture one legitimate webhook `(raw_body, hmac)` pair from their own store, then replay it to the app's public webhook endpoint with the `shop-domain` header swapped to a victim shop, and/or the `topic`/`webhook-id` headers altered. `Registry.process` will accept it (HMAC checks out) and dispatch it to the handler tagged with the attacker-chosen `shop`/`topic`, causing the host application — which relies on this gem's stated guarantee that `HmacValidator.validate` authenticates the webhook — to process forged data as if it originated from another tenant. This is a cross-tenant data/identity confusion: the app may create, update, or redact records under a different shop's namespace based on attacker-controlled headers, satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any developer using this gem for webhook processing (a documented, first-class API — `ShopifyAPI::Webhooks::Registry.process` / `Request.new`) is affected. The prerequisite (being able to install the app once to obtain a valid HMAC/body pair) is unprivileged and requires no special access, secrets, or social engineering — only a normal merchant install, which is the gem's own expected usage flow.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` (or at minimum `shop-domain`) in the HMAC-signable string in `Request#to_signable_string`, or otherwise cryptographically bind them to the payload, so that `HmacValidator.validate` authenticates the full identity tuple used for routing, not just the raw body bytes.

### Proof of Concept
1. Install the target app (using this gem) on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic the app is registered for (e.g. `orders/create`) and capture the raw POST body and its `X-Shopify-Hmac-Sha256` header — this is a valid `(body, hmac)` pair under the app's shared `api_secret_key`.
2. Replay this exact `(body, hmac)` to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL.secure_compare(computed_signature, hmac)` against the raw body — this passes since the body/hmac pair is genuinely valid [6](#0-5) .
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` even though the payload actually belongs to the attacker's own shop, and the handler processes it as victim-tenant data [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
