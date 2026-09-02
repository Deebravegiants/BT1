### Title
Webhook `shop` Identity Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` attribute that downstream application code uses to identify the tenant is taken from an HTTP header that is never included in the signed payload. `Registry.process` validates only the body's HMAC and then hands the header-derived, unauthenticated `shop` value straight to the app's webhook handler. This breaks the identity binding: `authenticated_bytes == raw_body` but `trusted_tenant == header["shop-domain"]`, and these two are never bound together.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from an HTTP header with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Webhooks::Registry.process` calls this HMAC check, then immediately forwards `request.shop` (the unauthenticated header value) to the application's handler as the tenant identifier: [4](#0-3) 

Because the `api_secret_key` is shared across every shop that installs the app, any merchant (an ordinary, unprivileged internet user who installs the app on their own store) legitimately receives real, validly-signed webhooks for their own shop. Since the signature is computed over `@raw_body` alone, that same `(raw_body, hmac)` pair remains valid no matter what `shopify-shop-domain` / `x-shopify-shop-domain` header value is sent alongside it — the header is not part of the signed material. An attacker can therefore POST that untouched, still-validly-signed body to the app's public webhook endpoint while substituting an arbitrary victim shop domain in the shop header, and `Registry.process` will accept it and hand `WebhookMetadata` for the *victim's* shop to the handler.

This is the direct structural analog of the reported bug class: just as the audited protocol failed to bind "long token" and "short token" so that two conceptually distinct identifiers could be set equal (double counting funds), this library fails to bind the cryptographically-authenticated payload to the tenant identifier it hands to the application, allowing an attacker to set them to different, attacker-chosen shops.

### Impact Explanation
Any app built on this gem that trusts `WebhookMetadata#shop` (as the documented API and `Registry.process` implementation both encourage) to determine which merchant's session/access token to use, or which tenant's data to update, can be tricked into processing attacker-controlled payload content under a victim shop's identity — a cross-tenant access issue. This matches the Critical/High impact bar for "cross-tenant access."

### Likelihood Explanation
The barrier to obtaining a validly-signed body is low: any unprivileged user can install the app on a shop they control and thereby harvest one or more legitimately-signed `(raw_body, hmac)` pairs from real Shopify-delivered webhooks. Replaying that exact body against the app's public webhook endpoint with a substituted `shop` header requires no secret, TLS interception, or privileged access — only the ability to send an HTTP request, which is exactly the unprivileged-internet-user threat model in scope.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) values into the signed material that `HmacValidator` verifies, or otherwise cryptographically tie the header-derived shop domain to the payload before exposing it via `WebhookMetadata`. At minimum, `Webhooks::Registry.process` should independently corroborate `request.shop` against known/registered shop state before dispatching to handlers, rather than trusting an unauthenticated header verbatim.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g. `orders/create`) to the app's public webhook URL, capturing the full raw body and the `x-shopify-hmac-sha256` header Shopify computed with the shared `api_secret_key`.
2. Attacker resends the identical raw body and identical `x-shopify-hmac-sha256` value to the same public webhook endpoint, but changes `x-shopify-shop-domain` (or `shopify-shop-domain`) to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (the body only) and it matches, so `Registry.process` proceeds: [4](#0-3) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from and describes the attacker's own shop, letting the attacker inject/spoof data under the victim tenant's identity in any app logic keyed on `data.shop`.

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
