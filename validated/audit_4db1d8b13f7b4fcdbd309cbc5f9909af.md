Found a concrete analog matching the report's bug class (a check that doesn't cover/bind the value later trusted): the webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) header is **not covered by the HMAC signature** in this gem's webhook processing path.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values — which are read straight from unauthenticated HTTP headers and then handed to the app's handler as the trusted merchant/tenant identity — are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic binding: [2](#0-1) .

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`: [3](#0-2) . Since `to_signable_string` for a webhook request is just the raw body, the HMAC only proves "this body byte-string was signed by Shopify with the app's secret" — it says nothing about which shop, topic, or webhook this body was originally sent for.

`Registry.process` uses this weak binding to build trusted metadata for the handler: it validates the HMAC, then constructs `WebhookMetadata` directly from the same unauthenticated headers (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`): [4](#0-3) .

The broken identity binding, stated as an equality that should hold but doesn't:
`shop authenticated by HMAC` (nothing — HMAC only covers body bytes) ≠ `shop trusted by the handler as data.shop` (attacker-controlled header value).

### Impact Explanation
An attacker who has legitimately installed the app on their own store (unprivileged w.r.t. any other merchant) will receive real, validly-signed webhooks from Shopify for their own shop. Because the signature covers only the body, the attacker can replay that exact `(body, hmac-sha256)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with an arbitrary victim shop's domain or a different topic. `HmacValidator.validate` still succeeds (body unchanged), and `Registry.process` dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen value and/or a different topic than what was actually signed. Any host application that uses `data.shop` (or `data.topic`) to key merchant-scoped data (order sync, inventory writes, per-tenant state updates, deletion webhooks, etc.) can be made to attribute attacker-controlled body content to another tenant — a cross-tenant data-integrity/confusion primitive squarely inside this gem's own trust boundary (`Registry.process` + `HmacValidator`), not merely "host ignores the API".

### Likelihood Explanation
Requires the attacker to have (or create) at least one legitimate app installation to obtain a valid `(body, hmac)` pair — realistic for any public/free-to-install app, and the resulting request forgery against the webhook endpoint needs no credentials, no TLS interception, and no access to `client_secret`.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signed material (`to_signable_string`) for `ShopifyAPI::Webhooks::Request`, or otherwise verify these header values against an out-of-band trusted source (e.g., cross-check `shop` against a known/registered shop list) before constructing `WebhookMetadata`, so that the HMAC binds the entire tuple `(shop, topic, webhook_id, api_version, body)` rather than the body alone.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic (e.g. `orders/create`) and capture the raw request: `body`, `X-Shopify-Hmac-Sha256`, `X-Shopify-Topic`.
2. Construct a new HTTP POST to the app's webhook endpoint with the identical `body` and `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`@raw_body`) — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` — the app now processes attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
