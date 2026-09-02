### Title
Cross-Tenant Webhook Spoofing via `shop-domain` Header Not Bound by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only proves the *body* was signed by the app's shared secret [2](#0-1) . The `shop-domain`, `topic`, and `webhook-id` headers that are used to attribute and route the webhook to a specific merchant/tenant are read straight from unauthenticated headers [3](#0-2)  and are never included in the signed bytes, breaking the binding `shop_header == shop_that_signed_the_body`.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field [4](#0-3) . For webhooks, `to_signable_string` is defined as `@raw_body` only [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all pulled from HTTP headers that carry no cryptographic binding to the signed payload [5](#0-4) .

`Registry.process` validates only this body HMAC and then forwards `request.shop`, `request.topic`, and `request.parsed_body` (parsed from the *same* signed bytes) straight into the handler with no cross-check that the header-derived shop was actually the shop the payload was signed for [2](#0-1) .

Because the `api_secret_key` used to compute the HMAC is the single shared secret for the whole app (identical for every merchant installation) [6](#0-5) , any unprivileged user who installs the app on their own (free/dev) store can generate a genuine webhook delivery with a body they fully control (e.g. an `orders/create` payload with attacker-chosen note/line-item fields) and a correspondingly valid HMAC. Since the HMAC never covers the `shop-domain` header, that same body+HMAC pair remains valid if replayed to the app's public webhook endpoint with the `shop-domain` (and/or `topic`) header rewritten to point at an arbitrary victim shop. `Registry.process` will accept it and dispatch attacker-controlled data to the handler under the victim's shop identity [7](#0-6) .

### Impact Explanation
This breaks the tenant isolation the HMAC is meant to guarantee: an unprivileged attacker (who only needs their own store install, no leaked credentials) can make the app process forged event data attributed to a shop they do not control, i.e. cross-tenant access/data injection — matching the "Critical: cross-tenant access" impact tier.

### Likelihood Explanation
Likelihood is high for any app relying solely on `HmacValidator`/`Registry.process` (the documented path in this gem) without independently confirming the `shop` header against a known/expected shop list before trusting webhook content. Obtaining a valid signed body only requires installing the target app on any store, which is trivially available to any internet user.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind `request.shop` to the verified body before it is handed to the webhook handler in `Registry.process`. At minimum, document and/or enforce that callers must cross-check `request.shop` against their own list of installed shops before trusting a webhook payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own free dev store (`attacker.myshopify.com`), giving them the shared `api_secret_key`-signed webhook delivery mechanism.
2. Attacker triggers a real event (e.g. creates an order with attacker-crafted body) and captures the resulting HTTP request: raw JSON body `B` plus header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker replays this exact body `B` and HMAC header to the target app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the HMAC [8](#0-7) ; `Registry.process` then invokes the handler with `shop: "victim.myshopify.com"` and the attacker-controlled body [9](#0-8) , causing the app to act on forged data as if it came from the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
