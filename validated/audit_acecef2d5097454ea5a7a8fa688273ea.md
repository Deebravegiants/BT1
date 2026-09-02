### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook forgery via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used to route and attribute the webhook event are taken from unauthenticated HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body+HMAC pair is valid and then dispatches to the handler using the header-derived `shop`, without any check that this `shop` matches the tenant the body/signature actually belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or signature: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the HMAC over `to_signable_string` (the body), so it can never detect that the `shop` header has been altered: [3](#0-2) 

`Registry.process` treats a passing `HmacValidator.validate` result as full authentication of the webhook and then forwards `request.shop` directly to the app's handler as the tenant identity for the event: [4](#0-3) 

The identity binding that should hold is:
`shop_that_signed_the_body == shop_the_handler_is_told_the_event_belongs_to`

But the gem only enforces:
`hmac(body, api_secret_key) == received_hmac`

with no constraint tying that check to the `shop` header value. Since the webhook secret (`Context.api_secret_key`) is shared across every shop that installs the app (it is not per-shop), any actor who can install the app on one shop (a normal, unprivileged action for a public app) legitimately receives at least one `(raw_body, valid_hmac)` pair for their own shop. Because the `shop` header is outside the signed data, that same `(raw_body, hmac)` pair remains valid when replayed against the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header value pointing at a different, victim shop that also has the app installed. `Registry.process` will accept it (the HMAC check only looks at the body) and hand the handler `WebhookMetadata` claiming the event is `shop: <victim-shop>` while it actually carries the attacker's own shop's data.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce: an app that keys its persistence, side effects, or authorization decisions off `WebhookMetadata#shop` (the intended way to consume this API) can be made to apply attacker-controlled data/events to a different merchant's tenant record, without ever needing that merchant's credentials. This is a cross-tenant access issue reachable purely through the gem's own webhook verification code.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on any shop (a normal unprivileged action for any app that supports public installs), (2) capturing one legitimate `(body, x-shopify-hmac-sha256)` pair delivered to the attacker's own endpoint, and (3) POSTing it back to the app's public webhook endpoint with a different `shopify-shop-domain` header. No knowledge of `api_secret_key`, access tokens, or victim credentials is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind `request.shop` to the verified body — e.g., by having `HmacValidator`/`Request` build the signable string from a canonical combination of shop + body, or by having `Registry.process` independently verify that the `shop` header corresponds to a session/shop that is expected to receive this specific webhook payload before dispatching to handlers.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a legitimate delivery:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body B>`
   - Body: `B`
2. Resend the exact same body `B` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but replace the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks `body` vs `hmac`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the app handler with `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)`, causing the app to process attacker-controlled data as if it belonged to `victim.myshopify.com`.

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
