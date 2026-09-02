### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signable string from the raw request body only, while the shop identity (`x-shopify-shop-domain` / `shopify-shop-domain` header) is read separately and never included in the HMAC-covered material. `Registry.process` trusts this unauthenticated `shop` value and forwards it directly into the handler's `WebhookMetadata`, breaking the binding between "the tenant whose HMAC was verified" and "the tenant the app believes sent the event."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from a header that is completely outside that signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the body) against the computed HMAC: [3](#0-2) 

`Registry.process` performs this HMAC check, then unconditionally trusts `request.shop` for dispatch, without any additional binding to a known/expected shop: [4](#0-3) 

The equality this design assumes is: `shop_authenticated_by_hmac == shop_used_by_handler`. In reality, the HMAC only authenticates `raw_body`, so the equality that actually holds is `hmac_verifies(raw_body) ⇒ body_is_untampered`, with `shop`, `topic`, and `webhook_id` all supplied via unauthenticated headers. Since handler lookup itself is keyed purely by `topic` (`@registry[request.topic]&.handler`) with no per-shop scoping, an attacker who possesses any one valid `(raw_body, hmac)` pair for a given topic (e.g., from a webhook legitimately delivered to their own shop after installing the app) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` still succeeds because it never inspects the shop header, and the handler receives `WebhookMetadata` claiming the event originated from the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler acts on data while believing it came from a shop it never actually verified. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up that shop's stored session/access token, updating that shop's local records, billing, or triggering shop-scoped side effects), an attacker who owns one shop with the app installed can inject events that are processed as if belonging to a different (potentially victim) shop, since the gem provides no protection against this at the HMAC-verification layer. This matches the Critical category of cross-tenant access.

### Likelihood Explanation
Exploitability requires only a legitimately obtained `(body, hmac)` pair, which any merchant who installs the app can generate for themselves (e.g., by triggering an `orders/create` or similar webhook on their own store) — no `api_secret_key`, access token, or privileged account is needed. The header is trivially replaceable in a replayed HTTP request. The gem does nothing to bind body-HMAC verification to the claimed shop, so likelihood is high wherever the host application relies on `WebhookMetadata#shop` as an authenticated tenant identifier.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the material verified against the HMAC, or require the host application to independently verify that `request.shop` corresponds to a shop with a currently registered webhook subscription/session before trusting it. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically bound to the verified HMAC and must not be treated as authenticated on its own.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook for topic `orders/create`; Shopify delivers a request with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's real `api_secret_key`.
2. Attacker captures the raw body and HMAC header value.
3. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (the unchanged raw body) against the HMAC — see: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes the attacker's data as if it originated from the victim shop.

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
