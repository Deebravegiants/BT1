### Title
Webhook Shop/Topic Identity Not Bound by HMAC, Enabling Cross-Tenant Webhook Forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from unauthenticated HTTP headers, while `to_signable_string` (the value verified by the HMAC) returns only the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` and `request.topic` to attribute the delivered payload to a tenant and dispatch a handler, without those fields ever being covered by the HMAC signature that `Utils::HmacValidator.validate` checks.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` and `x-shopify-topic`/`shopify-topic` headers, which are never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes `HMAC(secret, to_signable_string)` and compares it to the supplied hmac header — it never touches `shop`, `topic`, `api_version` or `webhook_id`: [3](#0-2) 

`Registry.process` then uses the unauthenticated `request.shop` and `request.topic` to select the handler and to build the tenant-identifying `WebhookMetadata` passed into application code: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`hmac_signed(shop_header) == shop_header_used_for_tenant_attribution`
In reality: `hmac_signed(raw_body only) ⊄ {shop_header, topic_header}`, so `shop_header` and `topic_header` can be swapped freely while the HMAC check still passes.

Because a single app's `client_secret`/`api_secret_key` is shared across every shop that installs that app, any unprivileged merchant who installs the app on their own store legitimately receives valid `(raw_body, hmac)` pairs for their own webhooks. That merchant can then replay the same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic` header) with any other shop that also has the app installed. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will dispatch the handler believing the event came from the victim shop with the attacker-chosen topic.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook delivery. An attacker-controlled shop can forge webhook events "signed for" a victim shop, causing the host application's handler code to execute business logic (e.g., data sync, GDPR redaction handling, order/customer processing) attributed to a shop the attacker doesn't own — a cross-tenant integrity violation rooted entirely in this gem's `Request`/`HmacValidator`/`Registry` implementation, not requiring any secret leakage or privileged access.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate, unprivileged merchant who installs the target app on their own store (which they can freely do), capture one legitimate webhook delivery from Shopify to their own endpoint, and replay it with modified `shop`/`topic` headers. No credentials, tokens, or `api_secret_key` need to be obtained — the HMAC check trivially passes because it never covers those headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (`to_signable_string`), or independently bind `request.shop` to a shop the application already trusts (e.g., verify it corresponds to a shop with a known, previously-stored session/installation) before dispatching to a handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, receiving a legitimately signed webhook: `raw_body`, `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
2. Attacker resends the exact same request to the app's webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers; `Utils::HmacValidator.validate(request)` recomputes HMAC over `raw_body` only (per `to_signable_string`) and it matches `H`, so validation passes: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the host application to process attacker-supplied data as if it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
