### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only and then forwards the header-derived `shop` value, unchanged, into the handler as the tenant identity. This breaks the binding `shop_used_by_handler == shop_authenticated_by_hmac`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` only, so the HMAC (`hmac-sha256` header, verified in `HmacValidator.validate`) authenticates just the byte content of the body — it does not bind `shop`, `topic`, `webhook_id`, or `api_version`, which are all pulled straight from request headers: [3](#0-2) 

`Registry.process` performs the HMAC check on the request, then immediately trusts `request.shop` (and `request.topic`, etc.) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Because every shop that installs the app shares the same `api_secret_key`, and because the `shop-domain` header sits entirely outside the signed content, a valid `(raw_body, hmac)` pair generated for one shop is equally "valid" when replayed with a different `shop-domain` header. The gem gives the caller no way to know the `shop` value was ever authenticated — the equality `shop_bound_by_hmac == shop_delivered_to_handler` does not hold, since the left side is undefined (no shop is bound by the signature at all).

### Impact Explanation
This is a cross-tenant identity confusion: the webhook handler (built on top of `WebhookMetadata#shop`) has no cryptographic assurance that the event actually originated from the shop it believes it did. Any app that keys per-shop side effects (session/token lookups, data writes, deletions, billing, notifications) off `WebhookMetadata#shop` can be made to act on the wrong tenant's data using only a body/HMAC pair obtainable by installing the app on an attacker-controlled shop. This matches the Critical "cross-tenant access" impact category — the gem hands the host application a shop identity that was never actually verified against the signed bytes.

### Likelihood Explanation
Any developer who installs this app on their own Shopify store (a normal, unprivileged action) can trigger arbitrary webhook topics against their own store, capture the resulting `raw_body` + `hmac-sha256` header (both delivered over HTTPS to the app's public webhook endpoint), and replay that exact pair to the same endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged credential is required — only the ability to receive one's own legitimate webhook, which is a standard capability of any merchant/developer using the app.

### Recommendation
Bind `shop`, `topic`, and other identity-relevant header fields into the signed payload used for HMAC verification (e.g., include a canonicalized representation of the relevant headers, or independently verify the `shop-domain` header against a shop that is known to have installed the app and cross-check it via a separate authenticated channel, such as the previously stored offline session for that shop) instead of trusting header values that sit outside the HMAC-covered bytes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) on their own shop and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent to the app's webhook endpoint.
3. Attacker replays the identical body and `hmac-sha256` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) — this succeeds because the body/HMAC pair is legitimately signed with the shared `api_secret_key`.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: request.shop, ...)`, where `request.shop` is the attacker-forged `victim-shop.myshopify.com`, even though nothing about that value was ever authenticated.

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
