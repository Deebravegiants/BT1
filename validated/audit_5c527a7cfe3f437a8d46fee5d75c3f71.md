### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Registry.process` validates never covers the `shop`, `topic`, or `webhook_id` headers that the same request exposes and that get handed straight to the app's webhook handler as the tenant identifier.

### Finding Description
`Utils::HmacValidator.validate` recomputes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value with `OpenSSL.secure_compare` [1](#0-0) . For webhook requests, `to_signable_string` is defined to be just `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are never mixed into the signed string [2](#0-1) .

`Registry.process` validates only the body's HMAC and then unconditionally trusts `request.shop` and `request.topic` to build the `WebhookMetadata` passed to the host application's handler: [3](#0-2) 

This breaks the identity binding `shop_verified_by_hmac == shop_used_by_handler`: the bytes cryptographically verified (the body) are disjoint from the bytes used to select the tenant (`x-shopify-shop-domain` header). Contrast this with the OAuth flow, where `AuthQuery#to_signable_string` explicitly folds `shop` into the signed string, so `shop` there *is* bound to the HMAC [4](#0-3) . No equivalent binding exists for the webhook `shop` header.

### Impact Explanation
An attacker who has legitimately received any one valid `(raw_body, hmac)` pair for a registered topic (e.g., by installing the app on their own shop and triggering a real event) can replay that exact body/HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header for a victim shop. Because the signature check only covers `@raw_body`, the forged headers pass validation, and the host application's handler executes attacker-controlled webhook data attributed to a shop the attacker does not control — a cross-tenant identity confusion inside the gem's own webhook trust boundary.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one valid signed body for the target topic, which they can do without any privileged credentials by installing the app on their own development/trial store and capturing the resulting genuine webhook delivery (headers are attacker-visible/attacker-controlled once received, since the receiving endpoint is the attacker's own infrastructure in that step). No knowledge of `api_secret_key` is required.

### Recommendation
Bind the tenant-identifying headers (`shop`, `topic`, `webhook_id`) into the signed material verified in `Request#to_signable_string`, or otherwise cryptographically tie them to the HMAC (e.g., require the host application to cross-check `request.shop` against the specific delivery's registered subscription/shop before trusting it), so that the same equality binding enforced for OAuth's `shop` parameter is enforced for webhook headers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., `orders/create`), capturing the raw POST body and the genuine `x-shopify-hmac-sha256` value Shopify computed for that body.
2. Attacker resends that exact `(raw_body, hmac)` pair to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the secret [5](#0-4) ; `Registry.process` then calls the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content [6](#0-5) , causing the host app to act on the victim tenant using forged data.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
