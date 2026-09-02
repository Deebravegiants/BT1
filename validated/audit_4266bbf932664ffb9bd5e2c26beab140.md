### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body alone, while the shop identity (`shop`), `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then hands the unverified `shop` header directly to the application's webhook handler as the tenant identity. This breaks the binding: `HMAC(body) == valid` while `shop_header != shop_that_produced_that_body_and_signature`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are never part of the signed data: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the secret-derived HMAC: [3](#0-2) 

`Registry.process` checks that HMAC and then immediately trusts `request.shop` as the tenant identity passed to the host app's handler, with no further binding check between the verified body and the claimed shop: [4](#0-3) 

Because the shop domain is not part of what the HMAC covers, any party who can obtain one legitimately-signed `(body, hmac)` pair for the app (e.g., a merchant who installed the app on their own store and received a real webhook from Shopify) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`webhook-id`) header to name a different, victim shop. `Utils::HmacValidator.validate` still succeeds because it only checks the (unchanged) body bytes against the (unchanged) HMAC — it has no way to detect that the claimed shop differs from the shop the signature actually vouches for. The forged `shop` value then flows into `WebhookMetadata` and is delivered to the app's registered handler as authoritative tenant identity.

### Impact Explanation
This crosses a tenant boundary: the identity binding "HMAC-verified body ⇔ shop that produced it" is broken, letting an attacker who legitimately controls one installed shop inject events that a webhook handler will process as belonging to an arbitrary other shop (cross-tenant confusion), matching the Critical "cross-tenant access" impact category. Any host application logic keyed off `data.shop` (e.g. updating shop-scoped state, triggering shop-scoped side effects) can be manipulated to target a shop the attacker doesn't control.

### Likelihood Explanation
Requires only a valid, previously-received webhook body+HMAC pair from the attacker's own legitimately-installed shop instance — no `api_secret_key`, access token, or credential theft is required, and no TLS interception is needed since the header can be freely modified by anyone sending the HTTP request to the app's own public webhook endpoint.

### Recommendation
Bind the shop identity to the signed payload: include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them to the body), so that verification fails if any of these identity headers are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same request to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` (`B`) and it still matches `H`, so validation in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) passes.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is `"victim-shop.myshopify.com"` — an identity the HMAC never actually vouched for — and the handler processes the event as if it came from the victim shop.

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
