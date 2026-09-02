### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by HMAC-validating only the raw request body, but it then trusts the `X-Shopify-Shop-Domain` header — which is *not* part of that HMAC — as the tenant identifier passed to the app's handler. Because a single app's `client_secret` (used as the HMAC key) is shared across every shop that installs the app, any merchant who has installed the app can capture a valid `(body, hmac)` pair from their own tenant's webhook traffic and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, producing a webhook that the app will process as if it legitimately originated from the victim tenant.

### Finding Description
The webhook signature is computed exclusively over the raw HTTP body: [1](#0-0) 

`Request#shop`, which becomes the tenant key handed to the consuming app, is read from a header that plays no part in that computation: [2](#0-1) 

`Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (and the parsed body) to the registered handler, with no cross-check that the shop is the one the body/signature actually belongs to: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only compares the computed HMAC of `to_signable_string` (the raw body) against the received HMAC, using `Context.api_secret_key`, which is the same secret for every shop that has this app installed: [4](#0-3) 

This is the exact "field acted on but not covered by the HMAC" pattern: the signature authenticates *bytes of the body*, but the code treats the unauthenticated `shop-domain` header as an authenticated tenant identity binding: `shop_authenticated_by_hmac == shop_used_as_tenant_key` does not hold — the equality that should be enforced is broken because `shop` is never included in the signed payload.

### Impact Explanation
Because the app's `client_secret` (the HMAC key) is identical for all shops running the app, any attacker who legitimately installs the app on their own shop (a normal, unprivileged action) can obtain a valid `(body, hmac)` pair — either by reading their own inbound webhook request, or, for topics whose payload structure is predictable/attacker-influenced (e.g. `app/uninstalled`, `shop/redact`, or any webhook whose body content the attacker can influence via their own store data), by crafting a body and getting Sho

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
