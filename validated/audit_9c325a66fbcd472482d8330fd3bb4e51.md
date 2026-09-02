### Title
Webhook `shop` identity is trusted from an HMAC-unsigned header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read from HTTP headers that are never included in that signature. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally hands the unauthenticated `shop` header value to the app's webhook handler as the tenant identifier, breaking the binding *shop asserted in header == shop that produced the signed body*.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the signed body: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the raw body only): [3](#0-2) 

`Registry.process` validates that HMAC, then immediately builds `WebhookMetadata` using the header-derived, unsigned `request.shop` value and dispatches it to the app's handler as trusted tenant context: [4](#0-3) 

Because the signature covers only the body bytes, any party who has obtained one legitimately signed `(raw_body, hmac)` pair for the app's `client_secret` (for example, by installing the target app on their own store and receiving one webhook) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header for a victim store. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` passes the attacker-chosen `shop` straight into `WebhookMetadata`, which the host application uses as the tenant/session key to look up and act on data for that shop. This breaks the equality "shop that produced this signed body" == "shop the handler acts on".

### Impact Explanation
This allows cross-tenant confusion: an app that keys per-shop side effects (e.g., updating shop-scoped records, triggering shop-scoped fulfillment, revoking access, syncing data) off `WebhookMetadata#shop` can be made to apply an attacker-obtained payload against a different, victim shop identifier, entirely from the public internet and without any of the app's credentials. This matches the "cross-tenant access" impact category from a boundary the gem itself is responsible for enforcing (HMAC validation of inbound webhook identity).

### Likelihood Explanation
Requires only: (1) the ability to obtain a single valid signed webhook body from the target app (achievable by installing the app on an attacker-controlled shop, which many "webhooks" topics allow with minimal privilege), and (2) sending a crafted HTTP POST with a substituted `shop-domain` header to the app's public webhook endpoint. No leaked secrets, tokens, or privileged access are required — only the app's own willingness to accept webhook traffic, which is the gem's advertised entry point.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload verification, or require host applications to cross-check `request.shop` against an out-of-band trusted shop registry before trusting it. At minimum, `Utils::VerifiableQuery`/`HmacValidator` should bind the header-derived identity fields into the signable string used for verification, so a replayed body cannot be reattributed to a different shop.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`, triggering webhook topic `X` and capturing the resulting raw POST body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (signed with the app's real `client_secret`).
2. Attacker sends a POST to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-topic: X`, but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `HmacValidator.validate` computes the HMAC over `B` only and it matches `H`, so validation passes.
4. `Registry.process` dispatches `WebhookMetadata.new(topic: "X", shop: "victim.myshopify.com", body: parsed_body, ...)` to the app's handler, which processes attacker-controlled data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
