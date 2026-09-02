### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` attribute used to identify which merchant a webhook belongs to comes from an HTTP header that is never part of the signed bytes. Since the same `client_secret` (and therefore the same HMAC) is valid for every shop that has the app installed, any party who can obtain one legitimate `(body, hmac)` pair (e.g. by installing the app on their own shop and receiving their own webhooks) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Utils::HmacValidator` will still validate successfully, and `Webhooks::Registry.process` will invoke the app's handler attributing the (attacker-chosen) body to the victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is not fed into `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate`/`validate_signature` only checks the HMAC against `verifiable_query.to_signable_string`, i.e. the body — the `shop` header plays no role in the cryptographic check: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity passed to the app's handler: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the app, the equality the app relies on is:
`HMAC_valid(body) == true` ⟺ `shop == <the shop the body actually came from>`

This equality does not hold: `HMAC_valid(body)` is a function of `body` and the shared app secret only, independent of `shop`. An attacker who legitimately controls one tenant (their own installed shop) can capture a valid `(body, hmac)` pair from their own legitimate webhook traffic, then send an HTTP request to the app's webhook endpoint with that same body/HMAC but an arbitrary `x-shopify-shop-domain` header value (a victim sho

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
