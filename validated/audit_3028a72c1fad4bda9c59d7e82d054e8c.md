### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC digest exclusively over the raw request body [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values used to identify the tenant and dispatch the handler are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that the HMAC matches the body, then dispatches to the handler using the unverified `shop` header as the tenant identity [3](#0-2) .

### Finding Description
The identity binding broken here is: **`shop` used to authorize/identify the tenant == `shop` covered by the HMAC**. In this gem's implementation the equality does not hold — `hmac` in `HmacValidator.validate_signature` only recomputes `compute_signature(verifiable_query.to_signable_string, secret)`, and for the webhook `Request` class `to_signable_string` returns `@raw_body` only [4](#0-3) [1](#0-0) . The `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers are never part of the signed material, yet `Registry.process` forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight into `WebhookMetadata` handed to the app's handler [3](#0-2) .

Because the HMAC is a function of body bytes alone (using the app's own `client_secret`-derived `api_secret_key`), any attacker who can obtain one valid `(raw_body, hmac)` pair — e.g., by owning their own Shopify store, subscribing that store to the same webhook topic on the same app, and capturing the resulting webhook delivery — can replay that exact body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header (and/or `webhook-id`, `api-version`) with a different, victim shop's domain. `HmacValidator.validate` will still return `true` because the signed content (raw body) is unchanged, and the handler will process the payload believing it originated from the victim shop, i.e., a **cross-tenant** request lands in the wrong tenant's processing pipeline.

### Impact Explanation
This directly matches the "Critical - cross-tenant access" impact bucket: an unprivileged internet user (any merchant who installs/uses the app on their own store, which is an unprivileged relationship w.r.t. other tenants) can inject a payload that is processed as belonging to another shop, since the tenant-identifying `shop` field is not bound to the cryptographic proof of authenticity the gem exposes via `HmacValidator`/`VerifiableQuery`. Any host app that uses `WebhookMetadata#shop` (the documented, intended field for this purpose — see `Registry.process`) to key session lookup, database writes, or business logic for a given tenant can be made to attribute attacker-controlled data to a victim shop.

### Likelihood Explanation
Medium-to-High: it requires the attacker to control a legitimate installation of the target app (trivial for public apps — anyone can install a Shopify app on their own dev/test store) and to trigger a webhook event with body content they want replayed, then intercept and resend it with a modified `shop-domain` header value. No secret material, tokens, or privileged access is required — the entire path only depends on capabilities available to any ordinary internet user/merchant who can install the app.

### Recommendation
Bind the shop identity to the signed content. Concretely, extend `VerifiableQuery`/`to_signable_string` for `ShopifyAPI::Webhooks::Request` to canonically include the `shop-domain`, `topic`, `webhook-id`, and `api-version` header values in the signed material (or otherwise cryptographically bind them), so `HmacValidator.validate` fails if any of these are altered post-signing. Short of changing Shopify's wire format, at minimum document prominently in `ShopifyAPI::Webhooks::Request`/`Registry` that `shop`, `topic`, `webhook_id`, and `api_version` are **not** authenticated by the HMAC check and must not be trusted as tenant identifiers without additional verification (e.g., cross-checking against a known/registered shop list, or requiring TLS client identity).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and subscribes it to a webhook topic (e.g. `orders/create`) with body `B`.
2. Shopify sends a legitimate webhook to the app's endpoint:
   ```
   headers: {
     "x-shopify-topic": "orders/create",
     "x-shopify-hmac-sha256": "<valid-hmac-of-B>",
     "x-shopify-shop-domain": "attacker-shop.myshopify.com",
     ...
   }
   body: B
   ```
3. Attacker captures this request and replays it to the same endpoint, only changing the `shop-domain` header to `victim-shop.myshopify.com`, keeping body `B` and the HMAC identical:
   ```ruby
   ShopifyAPI::Webhooks::Request.new(
     raw_body: B,
     headers: { "x-shopify-topic" => "orders/create",
                "x-shopify-hmac-sha256" => "<valid-hmac-of-B>",
                "x-shopify-shop-domain" => "victim-shop.myshopify.com" }
   )
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` (per [5](#0-4) ) because only the body `B` is verified.
5. `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` [3](#0-2) , causing the app to process attacker-controlled data as if it originated from the victim's store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
