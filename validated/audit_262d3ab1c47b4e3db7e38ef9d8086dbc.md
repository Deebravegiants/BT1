I found a concrete analog: the webhook HMAC verification in this gem covers only the request body, not the `shop` (tenant) or `topic` header values that `Webhooks::Registry.process` trusts to route/attribute the payload.

### Title
Webhook HMAC does not bind the `shop`/`topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's `client_secret`. The `shop` and `topic` values, which are read from unauthenticated HTTP headers, are never part of the signed data yet are trusted as the tenant/topic identity by `Registry.process`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
while `shop` and `topic` are pulled straight from headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` then trusts `request.shop` (an unauthenticated header) as the tenant identity for the handler, after only checking the body HMAC: [4](#0-3) 

Since a single app has one `client_secret` shared across **all** shops that install it, any `(raw_body, hmac)` pair that is valid for one shop's webhook delivery is also valid HMAC-wise for a request claiming to originate from a *different* shop — because the shop identity was never part of the signed string. This breaks the intended equality: `hmac_valid_for(body) == webhook_genuinely_originated_from(shop_header)`. In reality `hmac_valid_for(body)` only proves `body` was signed by *this app's* secret for *some* shop, not that it belongs to the shop named in the `x-shopify-shop-domain` header.

### Impact Explanation
An unprivileged attacker who is simply a merchant running the app on their own shop (Shop B, no special privileges beyond a normal install) can capture a legitimately-signed `(body, hmac)` pair delivered to the app for Shop B's own events (e.g., by triggering an `orders/create` or a mandatory `customers/redact` event and observing their own webhook traffic — no interception of anyone else's traffic is required). They can then replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header to name a victim shop (Shop A). `HmacValidator.validate` still passes because it never checked the shop header, and `Registry.process` invokes the handler with `WebhookMetadata` claiming the payload is for Shop A. This is a cross-tenant confusion: attacker-controlled webhook content (including sensitive flows like mandatory GDPR `customers/redact`/`shop/redact` webhooks) gets attributed to and processed under a different, unrelated tenant, without ever obtaining that tenant's credentials.

### Likelihood Explanation
Any merchant who installs the app (a normal, unprivileged action) can generate valid signed payloads for their own shop and replay them with a different `shop-domain` header against the app's public webhook endpoint. No secret material, access token, or privileged access to the victim tenant is required.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-signed string, or otherwise cryptographically bind the shop identity to the payload (e.g., require the app to independently verify the shop against a known/installed-shop list before trusting `request.shop`), rather than relying solely on an HMAC over the raw body while trusting unauthenticated headers for tenant attribution.

### Proof of Concept
1. Merchant installs the app on Shop B and triggers/observes a webhook delivery, capturing `raw_body` and the `x-shopify-hmac-sha256` header value (both valid for the app's shared `client_secret`).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with the identical `raw_body` and `hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body bytes against the secret (`lib/shopify_api/utils/hmac_validator.rb`).
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-supplied content as if it came from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
