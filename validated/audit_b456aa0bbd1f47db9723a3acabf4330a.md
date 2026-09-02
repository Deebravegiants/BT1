### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers and never bound into the signed payload. This breaks the identity binding `hmac_covered_bytes == authenticated_shop`, allowing an attacker who obtains any one valid `(body, hmac)` pair for their own shop to replay it with a forged `shop-domain` header pointing at a different (victim) shop, and have `Registry.process` accept it as authentic for that victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from HTTP headers with no cryptographic tie to the signature: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. the body only) — see: [3](#0-2) 

Once the HMAC check passes, `Registry.process` builds `WebhookMetadata` directly from the unauthenticated `request.shop` header value and hands it to the host application's webhook handler: [4](#0-3) 

Because the signature never binds `shop`, an attacker who can obtain one legitimate `(raw_body, hmac)` pair (e.g., by triggering a webhook delivery to their own store — many topics such as `app/uninstalled`, `shop/update`, `customers/data_request` carry attacker-influenced or shop-agnostic bodies) can replay that exact body+hmac while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over `@raw_body`, and `Registry.process` will dispatch the handler with `data.shop` set to the attacker-chosen victim domain.

### Impact Explanation
Host applications built on this gem commonly use the `shop` value from `WebhookMetadata` as the tenant/session key to look up merchant records, access tokens, or app state (this is the documented purpose of the `shop` field on webhook payloads). Since the HMAC does not bind `shop` to the signed bytes, this enables cross-tenant confusion: an attacker can cause the host application to process webhook data under a victim shop's identity, potentially triggering shop-scoped side effects (e.g., data deletion routines for `customers/redact`/`shop/redact`, state resets tied to `app/uninstalled`) against a shop they do not control. This matches the Critical "cross-tenant access" impact category via a broken authentication/identity binding.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(body, hmac)` pair, which is trivially obtainable by installing the app on their own development/test store and receiving a real webhook delivery (no `api_secret_key` or privileged access needed — webhook payloads are delivered over the standard app installation flow available to any unprivileged developer/user). The header manipulation itself (setting `shopify-shop-domain` to an arbitrary value) requires no credentials since the header is not part of the verified signature. This is directly reachable through the gem's public `Registry.process` / `Request` API.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed payload verification, or otherwise cryptographically bind them to the request before trusting `request.shop` in `WebhookMetadata`. At minimum, document that the `shop` header is unauthenticated so host applications cannot rely on it for tenant identification, or require host applications to independently verify shop ownership before granting access to resources keyed by webhook `shop`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook for topic `shop/update` (or any topic with shop-independent body content), capturing `raw_body` and the valid `x-shopify-hmac-sha256` header.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - the same `raw_body`
   - the same `x-shopify-hmac-sha256` value
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: shop/update`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC — see [5](#0-4) .
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, causing the host application to process the webhook as originating from the victim shop.

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
