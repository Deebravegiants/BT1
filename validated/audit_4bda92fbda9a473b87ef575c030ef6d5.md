### Title
Webhook `shop` (and `topic`) identity is trusted from unauthenticated HTTP headers while the HMAC signature only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` only proves the *body bytes* are authentic. The `shop` (and `topic`) values that `Registry.process` hands to the app's webhook handler are read straight from HTTP headers and are never bound to that HMAC. An attacker who can produce (or capture) one valid `(body, hmac)` pair can replay it against the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header, and the signature check still passes, letting them impersonate any shop for that payload.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`; the `shop` accessor at line 21-23 reads the `shop-domain` header directly, completely independent of the signed content. `Registry.process` performs exactly one check, `Utils::HmacValidator.validate(request)`, then immediately forwards `request.shop` (the unauthenticated header) to the handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac`: [4](#0-3) 

Since `to_signable_string` == raw body only, the equality actually being enforced is:
`HMAC(secret, body) == received_hmac`

but the value trusted and propagated to the app is `shop = header["shopify-shop-domain"]`, which is **not** part of that equality. The binding the gem should be enforcing — `shop_that_produced_this_HMAC == shop_delivered_to_handler` — is broken: any `(body, hmac)` pair valid for shop A can be replayed with the `shop-domain`/`topic` headers rewritten to shop B, and it will still pass `Registry.process`, because those fields are never covered by the signature.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook delivery: the value handed to the app's handler as the webhook's shop of origin can be forged by any unprivileged party who obtains one legitimate `(body, hmac)` pair (e.g., from their own store's webhook traffic, which they legitimately receive as an app owner/merchant). The handler then processes attacker-chosen body content under an arbitrary victim shop identity — a cross-tenant confusion at the point the gem hands data off to the app, which maps to the Critical "cross-tenant access" category in scope.

### Likelihood Explanation
Medium-to-High: the attacker does not need `api_secret_key`, an access token, or network interception — they only need a valid `(body, hmac)` pair, which they can generate themselves by installing the app on their own shop and observing the webhooks Shopify sends them (or by controlling any shop the app is installed on and subscribing webhooks). They then send a forged HTTP POST directly to the app's public webhook endpoint with the same body/hmac but a different `x-shopify-shop-domain`/`x-shopify-topic` header.

### Recommendation
Include the tenant-identifying fields (`shop-domain`, and ideally `topic`/`webhook-id`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed body before `Registry.process` extracts `request.shop`/`request.topic`. At minimum, document loudly that `Request#shop`/`Request#topic` are NOT covered by `hmac` verification and must not be trusted as an authenticated tenant identifier by consuming applications.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and captures a legitimate webhook delivery: body `B`, header `x-shopify-hmac-sha256: H` (valid because `HMAC(secret, B) == H`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this still succeeds. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes body `B` as if it originated from the victim shop. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
