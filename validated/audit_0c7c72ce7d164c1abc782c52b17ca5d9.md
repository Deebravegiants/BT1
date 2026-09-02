### Title
Webhook shop/topic headers trusted for dispatch while HMAC only covers the request body - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, yet the `shop-domain` and `topic` headers — which are *not* covered by that HMAC — are trusted as-is and used to select the handler and build the `WebhookMetadata` object delivered to the app. This breaks the identity binding: `hmac(body) == valid` is verified, but `shop header == shop that produced this body` and `topic header == topic that produced this body` are never checked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The topic, shop, api-version and webhook-id are read straight from HTTP headers and are never folded into the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` (i.e., the body only) against the app's `api_secret_key`: [3](#0-2) 

`Registry.process` performs exactly this body-only check, then unconditionally trusts `request.topic` and `request.shop` to select the handler and construct the metadata object handed to the app's business logic: [4](#0-3) 

Because `shop` and `topic` are not part of the signable string, any body+hmac pair that was legitimately produced by Shopify for **one** shop/topic combination remains a cryptographically valid pair for **any** other shop/topic value an attacker chooses to place in the headers. The equality the code implicitly relies on — `hmac_valid(body) → (shop, topic) is authentic` — does not hold, because `hmac_valid(body)` only proves the body's integrity, not the header's provenance.

### Impact Explanation
An internet user who can install the target app on a shop they control (ordinary, unprivileged app installation — no special access to the *victim* required) can capture one authentic `(raw_body, X-Shopify-Hmac-Sha256)` pair from a real webhook delivered to their own store. That exact pair remains valid forever against `HmacValidator.validate`, regardless of the `X-Shopify-Shop-Domain` or `X-Shopify-Topic` header values sent alongside it. By replaying the same body/hmac to the app's public webhook endpoint with a forged `shop-domain` (pointing at a victim tenant) and/or a forged `topic` (routing the body to a different, more sensitive handler than the one that produced it), the attacker can make the app process attacker-influenced webhook content while impersonating a different shop or event type — a cross-tenant confusion inside the app's webhook processing pipeline that stems directly from this gem's `Registry.process`/`Webhooks::Request` design.

This satisfies the "cross-tenant access" criterion for Critical impact, since the gem's own code (not application misuse) is responsible for accepting and dispatching unauthenticated shop/topic metadata as if it were verified.

### Likelihood Explanation
Obtaining one authentic body+hmac sample only requires the attacker to install the app on any shop (their own), which is a standard, low-privilege action available to any developer/merchant with a Shopify Partner account — not the target's credentials, access token, or `client_secret`. No timestamp, nonce, or webhook_id replay-protection ties the hmac to a single delivery in this gem, so the captured pair can be reused indefinitely against the endpoint with arbitrary header values.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`) in the value that is HMAC-verified (or independently bind them, e.g., by requiring the app to look up the shop's own registered secret / webhook_id and rejecting mismatches), so that `HmacValidator.validate` proves the authenticity of the header metadata acted upon, not just the raw body bytes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a genuine webhook (e.g. `orders/create`), capturing the raw body `B` and its `X-Shopify-Hmac-Sha256` value `H` from the real Shopify delivery.
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because HMAC only covers `B`), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or `X-Shopify-Topic: <different-topic>`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `hmac(B)`: [5](#0-4) 
4. The app's handler receives a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` (or the forged topic) with attacker-controlled body content `B`, despite this data never having been produced or signed by Shopify for that shop/topic.

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
