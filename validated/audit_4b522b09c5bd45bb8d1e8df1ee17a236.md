I have enough evidence now to finalize the analysis.

### Title
Webhook `shop-domain` and `topic` headers are trusted by handlers without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` authenticates the byte content of the payload but never binds the `X-Shopify-Shop-Domain` or `X-Shopify-Topic` headers to that signature. `Registry.process` nonetheless takes `request.shop` and `request.topic` directly from the unauthenticated headers and hands them to the app's `WebhookHandler` as trusted identifiers.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `hmac`/`shop`/`topic` are all read straight from HTTP headers without any cryptographic linkage between them: [2](#0-1) 

`Registry.process` validates only this body-bound signature and then dispatches the handler using the unauthenticated `shop` and `topic` values: [3](#0-2) 

The `HmacValidator.validate` implementation confirms the signature check is performed strictly against `to_signable_string`, i.e., the body only: [4](#0-3) 

The identity binding this breaks is:
`shop_used_by_handler == shop_covered_by_hmac`
In reality, `shop_used_by_handler = header["x-shopify-shop-domain"]` while `shop_covered_by_hmac = ∅` (the HMAC only covers `@raw_body`). Any request whose body bytes match a signature the attacker legitimately possesses (e.g., from a webhook delivered to the attacker's own development/trial store) will pass `HmacValidator.validate` regardless of which `shop-domain` or `topic` header value is attached, because those fields are never part of the signed string.

### Impact Explanation
An attacker who controls or has access to any store that can receive a real webhook from Shopify (trivial to obtain via a free/trial store using the same app) can capture a `(raw_body, hmac)` pair that is valid under the app's `api_secret_key`. They can then replay that exact body to the victim application's webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a different, victim shop, and/or forging `X-Shopify-Topic` to a topic of their choosing. `Registry.process` will accept it as authentic (`Errors::InvalidWebhookError` is not raised) and will call the registered handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain and `topic` set to the attacker-chosen topic. Any host application that uses `data.shop` to look up per-tenant state, trigger tenant-scoped side effects, or as a security-relevant identifier (a documented, expected usage pattern shown in `docs/usage/webhooks.md`) will act on forged cross-tenant data, i.e. cross-tenant access/impersonation using a real signature the attacker legitimately holds for a different shop.

### Likelihood Explanation
Moderate-to-high: exploitation requires the attacker to have received one legitimate webhook to any shop connected to the target app (trivially obtainable by installing the app on a free development store), and then to replay that body with a rewritten `shop-domain`/`topic` header to the app's public webhook callback endpoint — no secrets, tokens, or privileged access are required beyond normal app installation.

### Recommendation
Include `shop`, `topic`, and ideally `webhook_id`/`api_version` in the value that is HMAC-verified, or independently verify that the `shop` value in the header corresponds to a shop that legitimately has this app installed (e.g., cross-check against stored shop/session records) before passing it to handlers. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC and must not be trusted as tenant identifiers without independent verification.

### Proof of Concept
1. Install the target app on an attacker-controlled development store `attacker.myshopify.com` and trigger a webhook (e.g. `orders/create`) to receive a real `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's `api_secret_key`.
2. Replay the captured request to the victim app's webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but set:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <topic of choice registered by the app>`
3. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)` over `@raw_body` only (`lib/shopify_api/utils/hmac_validator.rb:27-31`, `lib/shopify_api/webhooks/request.rb:35-38`), which succeeds since the body/hmac pair is unchanged.
4. The registered handler is invoked with `WebhookMetadata.new(topic: "<attacker-chosen>", shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled webhook content under the victim shop's identity.

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
