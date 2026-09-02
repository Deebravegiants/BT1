### Title
Webhook Shop/Topic/Webhook-ID Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that `Utils::HmacValidator` verifies against `X-Shopify-Hmac-Sha256` — is defined as the raw HTTP body only. The `shop`, `topic`, and `webhook_id` values that `Registry.process` subsequently trusts and hands to the app's webhook handler come from separate, unsigned HTTP headers. Verifying the body's HMAC therefore proves nothing about which shop, topic, or webhook the payload is for, breaking the binding `hmac_verified_bytes == identity_used_by_handler`.

### Finding Description
`Request#hmac` and `#to_signable_string` are the two methods required by `Utils::VerifiableQuery`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers (`shopify_header(...)`) and are never fed into the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` (and `validate_signature`) computes the HMAC purely over `to_signable_string`, i.e. purely over the raw body, using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` gates on that HMAC check and then dispatches the handler using the unauthenticated `request.topic` and `request.shop`: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop passed to WebhookMetadata`. Because the header carrying `shop` (and `topic`/`webhook_id`) is outside the signed data, the equality does not hold — the gem lets an attacker present a byte-identical, HMAC-valid body while attaching an arbitrary `shop`/`topic`/`webhook-id` header, and the library will report it as valid and forward the spoofed identity to the app.

Since `Context.api_secret_key` (the app's `client_secret`) is the same for every shop that has the app installed, any body+HMAC pair that is valid for one merchant's webhook delivery is also a valid signature for that same body regardless of which shop header is attached, because the header is never part of what's hashed.

### Impact Explanation
This is a cross-tenant identity-binding break inside the gem's own verification primitive (`Utils::HmacValidator` / `Webhooks::Request`), matching the Critical criteria of cross-tenant access: an app relying solely on `ShopifyAPI::Webhooks::Registry.process` to authenticate incoming webhooks receives no assurance that the `shop` (or `topic`/`webhook_id`) used for record lookups, redaction processing, tenant-scoped writes, etc. actually corresponds to the shop that produced the signed bytes. An attacker who can obtain a single legitimate `(raw_body, hmac)` pair for any topic (e.g., a topic they can trigger themselves in their own installed shop) can replay it with a forged `shopify-shop-domain` header pointing at a different tenant, causing the app to process/attribute that payload to the wrong shop.

### Likelihood Explanation
Any app built on this gem that follows the documented flow (`ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` + `Registry.process`) is affected, since the gem's own `hmac`/`to_signable_string` implementation intentionally excludes the shop/topic/webhook-id headers. No secret material or privileged access is required beyond obtaining one genuine webhook delivery (obtainable by any merchant who installs the app), making exploitation practical for any unprivileged, minimally-privileged app user.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material verified by `to_signable_string`/`HmacValidator`, or independently re-derive/validate `shop` from the parsed webhook body (most Shopify webhook payloads carry shop-scoped identifiers) before it is trusted for tenant-scoped processing in `Registry.process` / `WebhookMetadata`. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid since `H = HMAC(client_secret, B)`).
2. Attacker resends `raw_body: B`, headers `{ "x-shopify-hmac-sha256" => H, "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-topic" => <same or different topic>, "x-shopify-webhook-id" => <arbitrary> }` to the app's webhook endpoint.
3. `Webhooks::Request.new` accepts it (headers present); `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` — matches `H` because the shop header was never part of the signed string: [5](#0-4) 
4. `Registry.process` calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the app to act on `B`'s contents as if they belonged to `victim-shop.myshopify.com`. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
