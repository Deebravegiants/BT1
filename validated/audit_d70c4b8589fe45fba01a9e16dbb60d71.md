### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only. The `shop-domain` (tenant identity) header is read separately and is never part of the signed material, yet `ShopifyAPI::Webhooks::Registry.process` treats that unauthenticated header as the trusted tenant identifier and hands it straight to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC: [3](#0-2) 

`Registry.process` performs this body-only HMAC check and then immediately trusts `request.shop` as the tenant identity passed to the handler: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used for tenant routing`. Because the `shop-domain` header sits outside the signed payload, that equality does not hold — the signature only proves "this body was signed with the app's `client_secret`" (which is shared across *every* shop that installs the app), not "this body came from shop X."

### Impact Explanation
Any unprivileged party who can install the app on their own store (a trivial, unprivileged action — installing a public/dev app requires no special access) will receive genuine webhooks signed with the same shared `client_secret` used for all merchants of that app. They can capture a `(raw_body, hmac)` pair from their own store's webhook, then replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: request.shop, ...)` claiming to be the victim shop. Any host application logic that uses `data.shop` to select per-tenant state (e.g., look up session/access token, write per-tenant records, trigger side effects) can be tricked into acting on/for the wrong tenant — a cross-tenant identity confusion rooted entirely in this gem's `Webhooks::Request`/`Registry` implementation.

### Likelihood Explanation
Likelihood is high for any app that has multiple installs (the normal case for any public or multi-merchant app): obtaining one valid signed webhook body from an attacker-controlled shop is trivial (attacker just installs the app on their own store and triggers any webhook event), and replaying it with a modified `shop-domain` header requires nothing more than internet access to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material, or otherwise cryptographically verify the shop header against a value derived from Shopify's guarantees (e.g., cross-check `shop-domain` against the shop associated with the stored offline session used to register that specific webhook subscription, or require per-shop webhook secrets). At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a sole tenant key without additional verification, and consider raising in `Request`/`Registry` if a caller relies on `shop` before confirming it matches an expected/registered shop for the webhook subscription.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since `H = HMAC-SHA256(client_secret, B)`).
2. Attacker POSTs to the app's webhook endpoint:
   - Body: `B` (unchanged)
   - Headers: `X-Shopify-Hmac-Sha256: H` (unchanged), `X-Shopify-Topic: orders/create`, `X-Shopify-Shop-Domain: victim.myshopify.com` (changed)
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC-SHA256(client_secret, B) == H` — true.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, even though this data never originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
