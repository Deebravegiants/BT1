Found a genuine identity-binding gap: the webhook HMAC only covers the raw request body, while the `shop-domain` and `topic` headers used to route and attribute the payload are never included in the signed content.

### Title
Webhook HMAC does not bind the `shop-domain`/`topic` headers, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  which is what `Utils::HmacValidator.validate` verifies against the app's `client_secret`-derived HMAC [2](#0-1) . However, `Registry.process` trusts `request.shop` and `request.topic` — both read straight from HTTP headers, never part of the signed payload — to build the `WebhookMetadata` passed to the app's handler [3](#0-2) . The headers themselves come straight from `@headers`, with no cryptographic binding to the signature [4](#0-3) .

### Finding Description
The equality that should hold is: `shop/topic verified-by-HMAC == shop/topic acted-upon-by-handler`. In this gem that equality is broken — the HMAC only proves the body's integrity, not the `shop-domain` or `topic` headers that determine which tenant's data the handler dispatches to and how it's interpreted. An unprivileged internet user can obtain a fully valid `(raw_body, hmac)` pair by registering a webhook on any store they control (e.g., a free Shopify development store, an app that is installed on a shop they own), capturing the delivered webhook, and then replaying that exact body+HMAC to the target app's public webhook endpoint while substituting arbitrary `x-shopify-shop-domain` and `x-shopify-topic` header values. `Utils::HmacValidator.validate` will still pass since it only recomputes the HMAC over `@raw_body` [2](#0-1) , and `Registry.process` will hand the forged `shop`/`topic` straight to the registered handler as if it were an authentic Shopify-originated event for that shop/topic [3](#0-2) .

### Impact Explanation
Because host applications rely on `WebhookMetadata#shop` to scope processing to the correct tenant (merchant), an attacker can make the app apply another merchant's payload/data under their own or an arbitrary shop identity, or trigger processing of a topic handler with a mismatched body — a cross-tenant confusion at the gem level. This matches "Critical - cross-tenant access" in the impact taxonomy, since the app cannot distinguish a genuine webhook for shop A from an attacker-controlled body relabeled as shop A via header spoofing, all without any of the app's credentials being compromised.

### Likelihood Explanation
Likelihood is high for any app that trusts `request.shop`/`request.topic` without independently re-verifying them (which the gem does nothing to prevent or warn about) — the attacker only needs to control one legitimate shop installation of the target app (or a topic/webhook they can trigger) to harvest a valid `(body, hmac)` pair, then can freely replay it with forged headers against the same public endpoint.

### Recommendation
Include the `shop-domain` and `topic` (and ideally `webhook-id`, `api-version`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload, so that `Utils::HmacValidator.validate` fails if any of those headers are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook for topic `orders/create`.
2. Attacker triggers the event and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` and the app's secret).
3. Attacker resends this exact `B`/`H` to the target's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: customers/update`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes (verifies `B` and `H` only) [5](#0-4) , then dispatches `WebhookMetadata.new(topic: "customers/update", shop: "victim-shop.myshopify.com", body: parsed(B), ...)` to the app's handler, which processes `B` as if it legitimately belonged to `victim-shop.myshopify.com`.

### Citations

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
