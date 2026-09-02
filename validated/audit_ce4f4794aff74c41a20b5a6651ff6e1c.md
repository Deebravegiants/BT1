Confirmed: `WebhookMetadata.shop` is passed directly from `Request#shop` (the `shopify-shop-domain` header) to the handler, while the HMAC (`Request#to_signable_string`) only signs `@raw_body`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, but exposes a separate `shop` accessor sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` — unchecked against the signature — straight into `WebhookMetadata` that is handed to the app's webhook handler. This breaks the equality `shop authenticated by HMAC == shop attributed to the webhook payload`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [4](#0-3) 

`Request#shop` is read directly from the `shopify-shop-domain` header without any cryptographic binding to the HMAC: [5](#0-4) 

`HmacValidator.validate` only verifies the `hmac` against `to_signable_string` (the raw body), never incorporating `shop`: [6](#0-5) 

`Registry.process` validates this HMAC/body pair and then trusts `request.shop` as the tenant identity passed to the handler: [2](#0-1) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the same app (this is inherent to how Shopify apps work, not specific host-app behavior), any shop that installs the app can generate a valid `(raw_body, hmac)` pair for its own webhook events by triggering an event in its store and capturing the delivered webhook. That shop can then replay the identical raw body and HMAC to the app's webhook endpoint directly (bypassing Shopify's delivery infrastructure) while substituting an arbitrary value in the `shopify-shop-domain` header. `HmacValidator.validate` will still succeed because the signature only ever covered the body, and `Registry.process` will pass the attacker-chosen `shop` string straight to the handler's `WebhookMetadata#shop`. Any host application that uses `WebhookMetadata#shop` to select which tenant's data to update, upsert, or delete (the documented, intended use of this field) will act on the wrong tenant.

### Impact Explanation
This is a cross-tenant identity confusion: the gem asserts to the host application that a given (Shopify-validated) event body belongs to shop B, when it was actually forged by shop A. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up the target shop's session/access token to process the event, or writing incoming data keyed by shop domain), this enables an unprivileged, self-service app installer to cause the app to process/attribute another merchant's webhook processing under an arbitrary shop domain — a cross-tenant access primitive, satisfying the "cross-tenant access" Critical impact bucket.

### Likelihood Explanation
Any merchant who installs a public app is, from the app's perspective, an "unprivileged internet user" with no special credentials — they only need to trigger a normal store event (e.g., an order or product update) to obtain a valid `(body, hmac)` pair for their own shop, then POST it directly to the app's public webhook endpoint with a forged `shopify-shop-domain` header. No `api_secret_key`, access token, or `client_secret` needs to be known by the attacker; the app's own valid webhook signature for their own data does the work.

### Recommendation
Include the shop domain (and topic/webhook-id) inside the HMAC-signable string, or independently verify `request.shop` against the shop associated with the session/HMAC context before trusting it in `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` must never be used as the sole tenant selector without corroborating it against a value bound to the signature (or against a shop the app already trusts, e.g., one it has an existing offline session for).

### Proof of Concept
1. App AppX is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com` (both share the same `api_secret_key`/`client_secret` for AppX, as is standard for Shopify apps).
2. Attacker triggers a normal event (e.g. product update) on `attacker-shop.myshopify.com`, causing Shopify to deliver a webhook to AppX's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-for-body>`, and some raw JSON body.
3. Attacker captures this `(raw_body, hmac)` pair.
4. Attacker crafts a new HTTP POST to AppX's webhook endpoint using the same `raw_body` and `hmac`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the signature: [7](#0-6)  — then invokes the app handler with `shop: "victim-shop.myshopify.com"`: [8](#0-7) .
6. The host app processes attacker-controlled data under `victim-shop.myshopify.com`'s identity.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
