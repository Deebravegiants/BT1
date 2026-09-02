### Title
Webhook HMAC only signs the raw body, not the `shop-domain` header used for tenant routing, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (tenant identity) that gets forwarded to the handler is read from an HTTP header that is never included in that signable string. `Registry.process` validates the HMAC and then unconditionally trusts the header-derived `shop` value when dispatching to the handler, breaking the equality "shop verified == shop acted upon."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, which is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding: [4](#0-3) 

Because `shop` is not part of the signed bytes, an attacker who can obtain any single valid `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and capturing a real Shopify-delivered webhook) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `Utils::HmacValidator.validate` will report success (the body bytes and signature match), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to a shop the attacker does not own. This is the classic "bytes verified vs. bytes/field acted upon" identity-binding break: the HMAC verifies the body is untampered and came from someone with the client secret, but the code treats that same request as also authoritative for *which shop* the payload is about — the two are conflated at the `Registry.process` call site even though the header is completely outside the signature's scope.

### Impact Explanation
Any consuming application that uses `request.shop` from a processed webhook (as recommended by this gem's own `WebhookMetadata`) to select which merchant's records to update will process attacker-supplied data under a victim shop's identity. This is a cross-tenant confusion vulnerability: an attacker who only controls their own (possibly free/dev) shop installation can inject data attributed to a different, unrelated shop, because the gem's webhook verification does not bind the authenticated bytes to the shop that is later trusted for routing.

### Likelihood Explanation
The webhook endpoint is by design internet-reachable (Shopify itself delivers webhooks over public HTTPS POST), so nothing prevents an attacker from POSTing directly with forged headers. The only prerequisite is possession of one valid `(body, hmac)` pair signed with the app's `client_secret`, which any user who installs the app on their own store can trivially obtain from their own legitimate webhook deliveries.

### Recommendation
Include the tenant-identifying header (`shopify-shop-domain`) in the HMAC-signed bytes, or otherwise cryptographically bind the verified body to the shop before it is passed to `WebhookMetadata`/handlers, so that `to_signable_string` in `lib/shopify_api/webhooks/request.rb` covers all fields the application will act upon, not just the JSON body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook with raw body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's `client_secret`).
2. Attacker replays an HTTP POST to the app's public webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [5](#0-4) .
4. The handler is invoked with `WebhookMetadata` where `shop == "victim.myshopify.com"` even though `victim.myshopify.com` never sent this data [6](#0-5) .

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
