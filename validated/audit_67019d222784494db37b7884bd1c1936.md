### Title
Webhook HMAC only signs the raw body, not the `shop` header — allowing cross-tenant webhook replay/spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC signature it checks only binds the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler are read directly from HTTP headers that are never included in the signed payload, so they can be altered without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop`/`topic`/`webhook_id`/`api_version` are pulled straight from headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. the body bytes, and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` uses this HMAC check as its only authenticity gate, then immediately forwards `request.shop` (unauthenticated) to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop_bound_by_hmac == shop_delivered_to_handler`

In this implementation that equality is false: `shop_bound_by_hmac` is undefined (the shop header is outside the signed bytes), while `shop_delivered_to_handler` is whatever value the `x-shopify-shop-domain`/`shopify-shop-domain` header contains. The gem's own documentation asserts `process` "will verify the request did indeed come from Shopify" and its example handler uses `data.shop` directly for tenant-scoped work (`shop_domain: data.shop`), reinforcing that callers are expected to trust this field as authenticated — but it isn't.

### Impact Explanation
An attacker who can obtain one genuinely-signed webhook body+signature pair for the target app (trivially available to any attacker who installs the app on their own shop, since Shopify sends them real signed webhooks) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. The signature remains valid because it never covered that header. The host app's handler then processes attacker-controlled webhook content while believing it originated from a different, victim shop — a cross-tenant data-injection/confusion primitive that falls under "cross-tenant access," a Critical-impact category.

### Likelihood Explanation
Likelihood is high for any app that installs the app on any shop (including the attacker's own) and receives webhooks: no secrets, tokens, or privileged access are required beyond normal app installation, and the replay only requires capturing/observing one legitimately delivered webhook (attacker's own shop's webhook, which they trivially receive) and re-sending it with a modified header. No `api_secret_key`, access token, or TLS interception is needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) values into the signed material, or otherwise cross-validate `request.shop` against the specific shop(s) the app expects/has registered for before invoking the handler, rather than trusting the unauthenticated header. At minimum, update `HmacValidator`/`Webhooks::Request` so identity fields consumed by handlers are covered by the same cryptographic guarantee that the body enjoys.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) so Shopify delivers a genuine request with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC over `B`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture this request.
3. Replay the identical request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but rewrite `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes the HMAC over `B` only, which still matches `H`, so `Registry.process` passes the request to the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` — the app now acts on attacker-supplied data as if it belonged to the victim shop.

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
