### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via body replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks the HMAC over that signable string against `Context.api_secret_key` [3](#0-2) , so it never binds the claimed `shop` (the tenant the payload is attributed to) to the signature. `Registry.process` then trusts `request.shop` and `request.topic` verbatim to dispatch and tag the payload for a handler [4](#0-3) .

### Finding Description
The equality the gem is supposed to enforce is: `shop (cryptographically bound to this exact payload) == shop (the tenant identity acted upon by the handler)`. In this gem that equality never holds, because the HMAC only covers `@raw_body` [1](#0-0)  and the `shop`/`topic` headers are parsed independently and never mixed into the signature computation [2](#0-1) .

Any unprivileged internet user can create their own free Shopify development store, install a public/dev app that uses this gem, and trigger a real webhook delivery for their own shop. That delivery arrives with a *valid* HMAC computed by Shopify using the app's `client_secret` over the body only. Because the signature never incorporates the `shop-domain`, `topic`, or `webhook-id` headers, the attacker can replay the exact same `raw_body` + `hmac` pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain (and/or the `X-Shopify-Topic` header for a different, more sensitive topic). `Utils::HmacValidator.validate` will still return `true` [5](#0-4) , since it only re-derives the HMAC of the body and compares it to the (still valid) supplied HMAC — it never checks that the HMAC was meant for this `shop`/`topic` combination.

`Registry.process` then builds `WebhookMetadata` directly from the attacker-controlled `request.shop` / `request.topic` and passes it to the registered handler as if it were authenticated data for that tenant [4](#0-3) , breaking the tenant identity binding that host applications rely on this gem to enforce.

### Impact Explanation
This is a cross-tenant identity confusion at the library layer: the gem hands the host application attacker-chosen `shop`/`topic` values that it claims are HMAC-verified, when only the body bytes were actually verified. Any host application that uses `WebhookMetadata#shop` (e.g. to look up that shop's stored access token, update per-shop state, or route mandatory GDPR topics such as `customers/redact`/`shop/redact`) can be made to act on/for a shop the attacker does not control, using a payload the attacker fully authored for their own store. This matches the "cross-tenant access" class of Critical impact for this assessment.

### Likelihood Explanation
Likelihood is high for the primitive itself: no privileged credentials, access tokens, or `client_secret` knowledge are required — only a free Shopify store that can receive at least one real webhook delivery. Full exploitation impact depends on how a specific host application consumes `WebhookMetadata#shop`, but the gem itself provides no protection against this header/body identity mismatch, which is squarely inside `lib/shopify_api/webhooks/**` (in scope).

### Recommendation
Include the tenant-identifying and dispatch-relevant fields (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-covered signable string, or otherwise cryptographically bind them to the payload (e.g., require the host app to independently confirm `request.shop` belongs to a known, previously-authenticated session before trusting `WebhookMetadata`). At minimum, document prominently that `request.shop`/`request.topic` are NOT covered by `HmacValidator.validate` and must not be trusted for authorization decisions without additional verification (such as checking that a session/access token already exists for that exact shop).

### Proof of Concept
1. Attacker installs the target app (built with this gem) on their own store `attacker.myshopify.com` and lets Shopify deliver a real webhook, e.g. `orders/create`, capturing the raw POST body `B` and the valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` with the app's `client_secret`).
2. Attacker replays the request to the app's webhook endpoint, keeping `body = B` and `X-Shopify-Hmac-Sha256 = H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally changes `X-Shopify-Topic` to a different registered topic).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only [6](#0-5)  — it matches `H`, so validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: <attacker-chosen>, shop: "victim.myshopify.com", body: <attacker-authored>, ...)` [7](#0-6) , and the host application processes attacker-authored data as if it legitimately originated from `victim.myshopify.com`.

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
