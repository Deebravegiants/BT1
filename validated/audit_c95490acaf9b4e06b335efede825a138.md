### Title
Webhook `shop` (and other Shopify headers) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers. `Registry.process` trusts `request.shop` (and the other header-derived fields) as the tenant identity passed to the merchant's webhook handler, even though none of these fields are bound by the HMAC that is validated just one line earlier.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body, and `hmac` is read from the `hmac-sha256` header, but `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate, independent headers that are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (an unauthenticated header) to the application's handler as the tenant identifier, without any additional binding check between the signed body and the `shop` header: [3](#0-2) 

The binding the code implicitly assumes is: `hmac_valid(body) == true` implies `shop_header == shop_that_generated(body)`. That equality does not hold, because `shop` is outside the HMAC's scope. Since Shopify signs webhooks for *all* shops installed on a given app with the same `client_secret`, any merchant with the app installed receives their own legitimately-HMAC-signed webhook deliveries (valid body + valid hmac header for their own shop). Such a merchant — an unprivileged actor with respect to other tenants of the same app — can capture one of their own signed deliveries and replay the identical `body`/`hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain). `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata` reporting the attacker-chosen `shop`, `topic`, and `webhook_id`, decoupled from the actually-signed content.

### Impact Explanation
This breaks the tenant binding the HMAC is meant to enforce. Any host application that uses `request.shop` from `WebhookMetadata` to select which merchant's data/record to create, update, or delete based on webhook payloads is exposed to cross-tenant data confusion/write using another merchant's replayed-but-still-validly-signed payload, satisfying the Critical "cross-tenant access" impact category, since the identity field driving per-tenant logic is forgeable independently of the cryptographic check that is supposed to guarantee authenticity.

### Likelihood Explanation
Exploitation only requires being any single merchant that has the app installed (an unprivileged actor relative to other tenants) capturing one legitimate webhook delivery for their own shop and replaying it with a modified `shop-domain` header — no access to `api_secret_key`, access tokens, or the app's infrastructure is needed, and no TLS interception is required since the merchant is a legitimate recipient of their own webhook.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-covered string (or otherwise cryptographically bind them to the signed body), or require that `Registry.process` validate the header-derived `shop`/`topic` against values embedded in the signed payload before dispatching to handlers.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, both signed with the same `client_secret`.
2. Shopify delivers a webhook to the app for `shop-a`: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), header `x-shopify-shop-domain: shop-a.myshopify.com`.
3. An operator of `shop-a` (or anyone able to observe that delivery) resends the identical body `B` and `hmac-sha256: H`, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks `B` against `H`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app's handler with `WebhookMetadata.new(... shop: "shop-b.myshopify.com" ...)`, causing the app to act on `shop-b`'s tenant context using attacker-supplied data.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
