## Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` value used for tenant attribution is read from a separate, unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards this unauthenticated `shop` value straight to the app's handler. This breaks the identity binding `shop-authenticated == shop-used-for-tenant-routing`, letting an attacker who possesses one validly-signed webhook body replay it under an arbitrary shop domain.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, a field that is never included in what gets HMAC'd: [2](#0-1) 

`Registry.process` validates only the body/HMAC pair, then immediately trusts the unauthenticated `shop` header value to build the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms only that the signable string (the raw body) matches the HMAC, entirely independent of the `shop` header: [4](#0-3) 

So the equality the gem is supposed to guarantee — *the shop whose webhook was authenticated == the shop attributed to the delivered data* — does not actually hold: the HMAC authenticates bytes of the body, but the identity binding (`shop`) travels on a completely separate, unsigned channel. Any party holding one legitimately-signed webhook payload for their own shop can resend it to the app's webhook endpoint with the `shop-domain` header changed to any other shop, and the gem will report `Utils::HmacValidator.validate` as `true` and hand the forged shop identity to the handler.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler receives `data.shop` (per `WebhookMetadata`) claiming to be shop B while the actual authenticated bytes originated as a genuine webhook for shop A. Any host application that uses this gem's `request.shop` / `WebhookMetadata#shop` for tenant lookup, session selection, or authorization (which is the gem's own documented usage pattern, exercised directly in `Registry.process`) will act on forged tenant data, e.g., writing order/customer state into the wrong merchant's account. This matches the report's "identity binding broken by authentication vs. routing mismatch" bug class and rises to cross-tenant access.

### Likelihood Explanation
Any merchant/attacker who has legitimately installed the app on their own shop naturally receives real, correctly-signed webhooks at the app's endpoint (this requires no `api_secret_key`, no access token, and no privileged account — only normal, unprivileged use of the app as an installed merchant). Capturing and replaying one such payload with a modified `shop-domain` header is trivial and entirely reproducible using only the gem's public `Webhooks::Request` / `Webhooks::Registry.process` API.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the signed body, so that `HmacValidator.validate` fails if the `shop-domain` header is altered relative to the originally signed webhook. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant routing without an independent, authenticated cross-check (e.g., matching against the shop tied to the currently active session).

### Proof of Concept
1. App merchant "shop-a.myshopify.com" installs the app and receives a legitimate webhook, e.g. `orders/create`, correctly signed by Shopify with headers `x-shopify-hmac-sha256: <valid mac over raw body>`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`.
2. The merchant (or anyone who can intercept/replay this request to the app's public webhook endpoint) resends the exact same raw body and HMAC header, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "shop-b.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-199`), even though the payload was never actually sent by Shopify for shop B.

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
