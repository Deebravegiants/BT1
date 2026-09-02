### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` fields are not covered by the HMAC signature, allowing cross-tenant webhook data spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook-id`, and `api-version` values used to route and attribute the webhook are taken from unsigned HTTP headers. `Webhooks::Registry.process` trusts these header-derived values as the authoritative shop/topic identity once the body HMAC checks out, breaking the binding `hmac-authenticated shop == shop used by handler`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read directly from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively from `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) 

`Webhooks::Registry.process` validates only this body HMAC, then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values: [4](#0-3) 

Because the secret used to sign webhooks (`Context.api_secret_key`) is a single app-wide secret shared by every installed shop (not a per-shop secret), any body+HMAC pair that is valid for one shop's webhook delivery is also a valid HMAC for the same body attributed to a *different* shop, since the header carrying the shop identity is never included in the signed content. An entity that can obtain one legitimate `(raw_body, hmac)` pair (e.g., a second app installed on any shop receiving webhooks with predictable/attacker-controlled body content, such as an `app/uninstalled` or a custom-content webhook the attacker's own shop triggers) can replay that exact body and HMAC to the victim app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The HMAC check passes because only the body is verified, and the handler is invoked believing the data belongs to the spoofed shop.

### Impact Explanation
This breaks the identity binding "the shop that produced a validly-signed webhook body == the shop the app processes the webhook data for," enabling cross-tenant data injection/confusion: an attacker-controlled shop can cause the app to ingest or act on webhook payloads while impersonating an arbitrary victim shop domain. This falls under the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. The gem's `HmacValidator` and `Webhooks::Request` design guarantees that headers are never part of the signed content by construction, and `Webhooks::Registry.process` performs no secondary check that the header-derived `shop` matches anything else (e.g. a known/expected shop for that delivery). Any consumer relying solely on `WebhookMetadata#shop` from `Registry.process` (as the library's own webhooks documentation instructs) inherits this gap without any additional code.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed content, or otherwise cryptographically bind the header-derived shop to the verified payload — for example, by having `Webhooks::Request#to_signable_string` incorporate the `shop`, `topic`, and `webhook_id` headers rather than the body alone (matching Shopify's actual webhook signing scheme, which signs the raw body only for a *specific, single* combination the receiving endpoint should already know), and/or requiring callers to supply the expected shop for comparison before processing.

### Proof of Concept
1. App B (attacker) installs the same third-party application as App A and receives a legitimate webhook whose body is fully attacker-influenced (e.g., a `products/create` webhook they trigger on their own store `attacker.myshopify.com`), capturing `raw_body` and the `x-shopify-hmac-sha256` value.
2. Attacker sends a new HTTP request to the target app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)`, causing the app to process attacker data as if it originated from the victim shop.

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
