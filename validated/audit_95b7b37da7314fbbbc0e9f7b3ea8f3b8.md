## #Vulnerability Found

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. This breaks the equality `HMAC-verified bytes == bytes used to establish tenant identity`, allowing an attacker who possesses one validly-signed webhook payload to relabel it as originating from a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac` is read straight from the `hmac-sha256`/`x-shopify-hmac-sha256` header: [2](#0-1) 

`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over exactly `to_signable_string` (i.e., the body) with `Context.api_secret_key`: [3](#0-2) 

However, the `shop` identity that `Registry.process` hands to the app's webhook handler comes from the `shop-domain` header, which is never included in the signed material: [4](#0-3) [5](#0-4) 

Because the app's `api_secret_key` is shared across *all* shops that install the app (it is not shop-specific), any tenant that has the app installed can generate arbitrary bodies that Shopify will legitimately sign for their own shop (e.g., by triggering `orders/create`, `customers/create`, etc. with attacker-chosen content). The resulting `(raw_body, hmac)` pair is valid per `HmacValidator.validate`, satisfying `computed_signature == received_signature`, for *any* `shop-domain` header value, since that header is outside the signed scope. An attacker can then replay that exact `raw_body`/`hmac` pair with the `shop-domain` header rewritten to a victim shop, and `Registry.process` will accept it and dispatch `WebhookMetadata.new(... shop: request.shop ...)` with the attacker-controlled shop value, having only verified the body's integrity, not its tenant origin.

### Impact Explanation
This is a cross-tenant identity-binding failure: the value that host applications use to key merchant data, sessions, or side effects (`shop`) is not bound to the credential (`hmac`) that "proves" webhook authenticity. Any application that uses `WebhookMetadata#shop` to look up or mutate per-shop state, without independently re-validating that the shop is a legitimate registered/installed tenant, can be tricked into writing attacker-controlled webhook data under a victim shop's identity — a cross-tenant access primitive.

### Likelihood Explanation
Any developer/merchant who can install the app on their own store (a very low bar — often free, or a dev/partner sandbox store) can generate a validly HMAC-signed webhook body via ordinary store actions and then replay it over the app's public webhook endpoint with a forged `shop-domain` header. No credentials beyond an ordinary shop install are required, and the HMAC check as implemented provides no protection against this because the header is entirely outside the signed content.

### Recommendation
Bind the shop identity to the HMAC-verified data instead of trusting the unauthenticated header:
- Include the `shop-domain` header value in the signable string / verification input, or
- Cross-check `request.shop` against a shop the app has actually installed/authorized for (e.g. verify a stored, previously-established session/access-token record exists for that exact shop) before dispatching to the handler, and reject the webhook if it doesn't match.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body of their choosing.
2. Shopify computes and sends `X-Shopify-Hmac-Sha256` over that raw body using the app's shared `api_secret_key`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact same raw body and `hmac` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) hmac: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, despite the request never having been authenticated for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
