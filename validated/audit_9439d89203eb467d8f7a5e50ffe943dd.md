This confirms the vulnerability. The `Webhooks::Request#to_signable_string` method returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers [2](#0-1) . `Registry.process` validates only the HMAC over the raw body, then trusts `request.shop`, `request.topic`, and `request.webhook_id` from headers to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook HMAC covers only the raw body, letting the `shop-domain` header (tenant identity) be forged independently of the signed payload - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` by signing/verifying only the raw HTTP body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `webhook_id`, and `api_version` fields — all of which are trusted and forwarded to the merchant app's webhook handler as `WebhookMetadata` — are read straight from HTTP headers that are never included in the HMAC computation.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it against the `hmac` accessor [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, and `hmac` is parsed from the `X-Shopify-Hmac-Sha256` header [5](#0-4) . The equality the code implicitly assumes is:

`bytes HMAC-verified (raw_body)` == `identity fields acted upon (shop, topic, webhook_id, api_version)`

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled from separate, unsigned headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) [2](#0-1) . Nothing in the signable string binds the body's HMAC to those header values. `Registry.process` then trusts the header-derived `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` struct dispatched to the app's handler, after only checking that the HMAC over the body is valid [3](#0-2) . Any unprivileged merchant who installs the app receives genuine webhook deliveries (with a body and a correctly computed HMAC) for their own store. Because the HMAC never covers the `shop-domain` header, that merchant can capture one authentic `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header value (e.g., a victim's shop). The HMAC check still passes — it only verifies the body — while the shop identity used for tenant routing/data attribution is fully attacker-controlled.

### Impact Explanation
This breaks the binding between the cryptographically verified data (the body) and the tenant identity the host application uses to route/attribute that data (the `shop` field in `WebhookMetadata`). Any app that uses `data.shop` from the webhook handler to decide which merchant's records to update (exactly as shown in the gem's own webhook documentation example) can have another merchant's genuine webhook body attributed to, and processed as, a different shop — a cross-tenant data-integrity/exfiltration primitive using only a webhook payload the attacker legitimately received for their own installation. This matches the Critical "cross-tenant access" impact category: an unprivileged app installer can attribute arbitrary webhook payloads to any target shop domain without ever possessing that shop's or the app's secrets.

### Likelihood Explanation
Likelihood is high: no secret material is needed. An attacker only needs to install the target app on their own store (or observe/replay any webhook they legitimately received) and modify a single unauthenticated HTTP header before resending the request to the app's public webhook endpoint. The HMAC validation logic in this gem provides no protection against this because it was never designed to bind headers to the signature.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or otherwise the entire header set that downstream code trusts) in the signable representation, or at minimum document/enforce that `shop-domain` must be independently corroborated (e.g., against the shop that owns the currently active session/subscription) before being used for tenant attribution. Since Shopify's actual HMAC scheme only ever signs the body, the safer fix belongs in `Registry.process`/`WebhookMetadata` consumers: require callers to cross-check `request.shop` against a known/expected shop for the subscription being processed rather than trusting the header value outright.

### Proof of Concept
1. App installs webhook handler that uses `data.shop` to select the tenant record to update, per the documented pattern in `docs/usage/webhooks.md` (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`).
2. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header `H` — both valid and delivered by Shopify.
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only re-hashes `B` [1](#0-0) ; `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [6](#0-5)  and forwards attacker-controlled order data as if it belonged to the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
