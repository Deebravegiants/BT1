Based on my investigation, I found a concrete instance of the reported bug class in this codebase.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC over the raw request body only, then hands the caller's `shop-domain`, `topic`, `api-version`, and `webhook-id` HTTP headers — none of which are covered by that HMAC — directly to the app's webhook handler as trusted identity fields.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header: [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and compares it to the received `hmac`: [2](#0-1) 

`Registry.process` performs this body-only HMAC check and, on success, builds `WebhookMetadata` straight from the request's `shop`, `topic`, `api_version`, and `webhook_id` accessors — all sourced from unauthenticated headers — and passes it to the registered handler: [3](#0-2) 

The identity binding that should hold is: `hmac-verified bytes == bytes the app treats as authoritative for shop/topic identity`. Here that equality is broken — the HMAC only proves the body wasn't tampered with; it proves nothing about which shop or topic the header values claim. `request.shop` (from `shopify-shop-domain`/`x-shopify-shop-domain`) is a field acted on (passed into `WebhookMetadata#shop`, which apps commonly use as the tenant key to look up sessions/data) but not covered by the HMAC.

### Impact Explanation
For a multi-tenant app with one webhook endpoint per app (the standard pattern), the shop identity delivered to the handler is not cryptographically bound to the payload. A party that receives a legitimate, validly-signed webhook for shop A (e.g., a merchant who installed the app, an unprivileged position relative to other tenants) can resend the same raw body to the app's webhook endpoint while substituting the `shop-domain` header for shop B. The HMAC still validates (it's computed only from the body, and the secret-derived signature for that exact body is unchanged), and `Registry.process` will invoke the handler with `shop: shop_B` alongside body data that actually belongs to shop A. If the host app trusts `WebhookMetadata#shop` as the tenant key without independently cross-checking a shop identifier embedded in the signed body, this yields cross-tenant data confusion/injection — one merchant can inject fabricated "events" attributed to another shop.

### Likelihood Explanation
Exploitability only requires possession of one genuine, previously-delivered webhook (body + valid HMAC) for the attacker's own shop — no `api_secret_key`, access token, or privileged access is needed. Any app merchant automatically has this. The header/body mismatch is fully controlled by the requester since `Registry.process` never cross-validates header-derived identity against anything inside the signed body.

### Recommendation
Do not treat header-derived `shop`, `topic`, `api_version`, or `webhook_id` as authoritative for tenant/identity decisions unless the payload itself contains a matching, expected shop identifier that the handler independently verifies (e.g., compare `request.shop` against a shop id/domain embedded in the JSON body, or against the shop tied to the session/webhook subscription the handler expects). At minimum, `Registry.process`/`WebhookMetadata` documentation should make explicit that `shop`/`topic` are unauthenticated and callers must not use them as a sole tenant-authorization key.

### Proof of Concept
1. App registers a webhook handler for topic `orders/create` used for shop `shop-a.myshopify.com`; the handler uses `data.shop` to route/store the order data per-tenant.
2. Shopify delivers a legitimate webhook for shop A: body `B`, headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Shop A's merchant (or anything with visibility into that delivery) resends the exact same body `B` and HMAC header to the app's webhook endpoint, but with `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `HMAC(secret, B)`, which is unchanged: [4](#0-3) 
5. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "shop-b.myshopify.com", body: <shop A's data>, ...)`, causing shop A's data to be processed under shop B's identity. [5](#0-4)

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
