### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` checks the HMAC solely against that body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken directly from unauthenticated HTTP headers — are never part of the signed data, yet `Registry.process` trusts `request.shop` as the tenant identity when constructing `WebhookMetadata` and dispatching to the host app's handler.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `webhook_id` are read straight from HTTP headers with no cryptographic binding to the signature: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature only from `to_signable_string` (the raw body) and compares it against the `hmac` header value; it never incorporates `shop`, `topic`, or `webhook_id`: [4](#0-3) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` as the source of truth for tenant identity, passing them into `WebhookMetadata` given to the host application's handler: [5](#0-4) [6](#0-5) 

This reproduces the reported bug class exactly: **a field acted on (the `shop` tenant identifier used to route/attribute the webhook payload) is not covered by the HMAC that is supposed to authenticate the request.** Every webhook for a given app is signed with the same app-level `client_secret` (`Context.api_secret_key`) regardless of which shop sent it — the secret is not shop-specific. Consequently, any actor who has legitimately received one valid `(raw_body, hmac)` pair from Shopify for their own shop (e.g., a merchant using the same app who registers a webhook and observes their own store's payload/HMAC) can replay that exact byte-identical body and HMAC value to the app's webhook endpoint while substituting a different `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header naming a victim shop. `HmacValidator.validate` will report the signature as valid (it never inspected the headers), and `Registry.process` will hand the host app a `WebhookMetadata` claiming the payload belongs to the victim shop.

The identity binding broken as an equality:
`shop_verified_by_hmac (∅, not signed) ≠ shop_used_for_tenant_attribution (request.shop, an unauthenticated header)`

### Impact Explanation
Because a validated webhook's declared `shop` is not guaranteed to be the shop the signature actually corresponds to, an app built on this gem that uses `WebhookMetadata#shop` to route data into the correct tenant's records (a documented and expected use of the field) can be made to attribute forged/replayed data to a shop the attacker does not control. This is a cross-tenant integrity/confusion issue: the receiving app's per-tenant data store can be polluted or manipulated using another merchant's webhook topic/body under a false shop identity, without possession of the app's `client_secret`, an access token, or any other privileged credential — only a single legitimate webhook capture from any shop using the app is required.

### Likelihood Explanation
Likelihood is high for any multi-tenant app: webhook payloads/HMACs are frequently observable by the shop-side (e.g., logged, inspected via browser devtools proxies, or captured by a malicious merchant installing the same app), and replaying an HTTP POST with modified headers to a public webhook endpoint requires no special access. No secret material needs to be recovered; the flaw is structural (headers excluded from the signed content) rather than cryptographic.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the data that is HMAC-verified, or otherwise cryptographically bind them to the signed payload (e.g., signing a canonical string that concatenates these header values with the body) before `Registry.process` treats `request.shop` as an authenticated tenant identifier. At minimum, document that `WebhookMetadata#shop`/`#topic` are NOT authenticated by `HmacValidator.validate` and must not be trusted for tenant routing without additional verification (e.g., cross-checking against a shop that is independently known to have an active session/subscription for that specific `webhook_id`).

### Proof of Concept
1. App "Acme" is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both signed with the same `Context.api_secret_key`.
2. Attacker, as a merchant on `attacker-shop.myshopify.com`, registers a webhook and captures a legitimate delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`), along with `X-Shopify-Topic: orders/create`.
3. Attacker sends `POST /webhooks` to the app with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `HmacValidator.validate` recomputes HMAC over `B` only, matching `H` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`).
5. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and dispatches to the host app's handler, which believes the (forged/replayed) order data came from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
