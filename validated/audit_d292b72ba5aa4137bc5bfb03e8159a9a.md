## Title
Webhook `shop` identity is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop` is read from a separate, unsigned header [2](#0-1) . `Utils::HmacValidator.validate` verifies the HMAC only over `to_signable_string`, meaning it cryptographically proves body integrity but says nothing about which shop the webhook is claimed to be for [3](#0-2) . `Registry.process` then trusts this unverified `request.shop` field to build the `WebhookMetadata` passed to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop domain used by the app's webhook handler == shop domain the HMAC signature actually authenticates`. In this gem it does not — the HMAC only authenticates `@raw_body` [5](#0-4) , and the `shop` accessor pulls straight from `x-shopify-shop-domain`/`shopify-shop-domain` headers without any cryptographic tie to the signature [2](#0-1) [6](#0-5) .

Additionally, `Context.api_secret_key` (and `old_api_secret_key`) is a single, global secret shared across every shop that installs the app [7](#0-6)  — it is not shop-specific. So a valid HMAC only proves "this body was signed with this app's client secret", not "this body/shop pairing came from Shopify for shop X".

Because of this, an unprivileged actor who legitimately installs the target app on their own shop (Shop A) will receive real, validly-signed webhooks for Shop A. They can replay that exact body (and therefore the exact valid HMAC) to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim's domain (Shop B). `HmacValidator.validate` will still pass because the signature check never touches the shop header [8](#0-7) , and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` even though the payload actually belongs to Shop A [9](#0-8) .

### Impact Explanation
Any host application relying on this gem's `Registry.process`/`HmacValidator.validate` to authenticate which tenant a webhook body belongs to is exposed to cross-tenant data confusion: an attacker-controlled shop's data can be attributed to, and processed against, a victim shop's session/store inside the app, since the shop identity is never bound to the signed content. This matches the Critical "cross-tenant access" category, as the library provides no mechanism to bind the authenticated bytes to the claimed tenant.

### Likelihood Explanation
Any user who can install the target Shopify app on their own store can obtain a validly-signed webhook body/HMAC pair, then trivially replay it with a forged `shop` header to the same public webhook endpoint — no access to `api_secret_key`, access tokens, or privileged accounts is required.

### Recommendation
Include the shop domain (and other identity-relevant fields such as topic/webhook-id) in the signable content used by `Utils::HmacValidator`, or otherwise cryptographically bind `request.shop` to the verified signature before it is handed to `Registry.process`/the app handler, so that the verified bytes and the identity acted upon are the same value.

### Proof of Concept
1. Install the target app on attacker-controlled Shop A; trigger any webhook topic the app subscribes to and capture the raw POST: headers (`x-shopify-hmac-sha256`, `x-shopify-shop-domain: shop-a.myshopify.com`, etc.) and raw body.
2. Resend the identical request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `shop-b.myshopify.com` (leave body and `x-shopify-hmac-sha256` untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` [1](#0-0)  — validation succeeds despite the forged shop header.
4. The registered handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and Shop A's body/data [9](#0-8) , causing the host app to act on Shop A's data under Shop B's tenant context.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
