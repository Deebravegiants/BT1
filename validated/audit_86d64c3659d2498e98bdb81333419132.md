Found: the critical binding in `ShopifyAPI::Webhooks::Registry.process` is that the webhook's `shop` (used to build `WebhookMetadata` and dispatched to the handler) comes from the unauthenticated `X-Shopify-Shop-Domain` header, and it is **not part of the HMAC-signed payload**.

### Title
Webhook `shop` identity is taken from an unauthenticated header, not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . `HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the body) against the app's secret [3](#0-2) , so the header carrying `shop` is never authenticated.

### Finding Description
`Registry.process` validates the HMAC over the request and then immediately trusts `request.shop` to construct `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the webhook: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) . Because `to_signable_string` for `Webhooks::Request` is just the raw body [1](#0-0) , the HMAC computed over `secret + raw_body` is identical no matter which `X-Shopify-Shop-Domain` header value accompanies it. Since a valid webhook payload/HMAC pair from shop A can be replayed with the `X-Shopify-Shop-Domain` header rewritten to shop B (headers are attacker-controlled at the HTTP layer and are not covered by the signature), the equality the library implicitly relies on — "HMAC-authenticated shop == shop delivered to the handler" — does not hold. The binding actually enforced is `HMAC(secret, raw_body) == received_hmac`, but the tenant identity used downstream is `header["x-shopify-shop-domain"]`, an entirely different, unauthenticated value.

### Impact Explanation
This breaks the cross-tenant boundary: an attacker who can capture or replay one valid signed webhook body (e.g. from a `write_products`-triggered webhook sent to a public endpoint, or via any other channel where a valid `(body, hmac)` pair becomes observable) can resubmit it with a different `shop-domain` header and cause the app's webhook handler to process/store data under an attacker-chosen shop, since `WebhookMetadata#shop` and thus the persisted/attributed session key [5](#0-4)  would come from the forged header. This is a cross-tenant identity binding failure matching the requested impact class.

### Likelihood Explanation
Exploitation requires the attacker to obtain a valid `(raw_body, hmac)` pair for some shop (this is realistic since webhook payloads are not secret — logs, error trackers, proxies, or a compromised/curious third party could observe them) and control of the delivery request to the app's webhook endpoint (which is normal for anyone able to POST to the public webhook URL). No possession of `api_secret_key` is required — only knowledge of a previously-delivered `(body, hmac)` pair.

### Recommendation
Include `shop-domain` (and ideally `topic`/`webhook-id`) in `to_signable_string`/the value the HMAC is computed over, or otherwise cryptographically bind the shop domain to the signed payload before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Observe a legitimately delivered webhook request to the app: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = H` (valid for shop `victim.myshopify.com`), since `to_signable_string` only depends on `B` [1](#0-0) .
2. Send a new POST to the app's webhook endpoint with the same `raw_body = B` and same `X-Shopify-Hmac-Sha256: H`, but with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over `B` [6](#0-5) .
4. `Registry.process` calls the handler with `shop: request.shop` = `"attacker.myshopify.com"` [5](#0-4) , even though the payload actually originated for `victim.myshopify.com`.

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
