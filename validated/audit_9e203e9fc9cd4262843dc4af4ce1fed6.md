I have sufficient evidence to write up the finding now.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from only the raw request body, while the `shop` identity used downstream by `ShopifyAPI::Webhooks::Registry.process` is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header. This breaks the identity binding `shop authenticated == shop acted upon`, letting an attacker who legitimately triggers one signed webhook (e.g., by installing the app on their own store) replay that same body/HMAC pair while substituting an arbitrary `shop-domain` header value, causing the host application's webhook handler to process attacker-controlled data as if it belonged to a different (victim) tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from an HTTP header that is never part of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then passes `request.shop` straight into the handler without any additional authentication of the shop identity: [3](#0-2) 

`HmacValidator.validate` confirms this: the signable string is whatever the `VerifiableQuery` (here, `Request#to_signable_string`, i.e., the raw body) returns — the shop header is simply not part of the equality being checked: [4](#0-3) 

Because HMAC-SHA256(body) is independent of the `shop-domain` header, any `(body, hmac)` pair that is valid for shop A remains a valid `(body, hmac)` pair no matter what value is placed in the `shop-domain` header. The equality the gem actually enforces is:
```
HMAC(raw_body, api_secret_key) == received_hmac
```
but the equality it should be enforcing (and silently fails to) is:
```
shop_the_hmac_was_issued_for == shop_the_handler_believes_it_is_processing_for
```
This is exactly the "field acted on but not covered by the HMAC" pattern: `request.shop` is acted upon (passed to `WebhookMetadata` and to the app's handler) but never cryptographically bound to the signature that was verified.

### Impact Explanation
An unprivileged attacker who can install the target app on their own (attacker-controlled) Shopify store is, by definition, a legitimate but low-privilege actor with respect to their own shop only. Any webhook Shopify sends for that install (e.g. `orders/create`, `app/uninstalled`, etc.) is a `(body, hmac)` pair the attacker can observe on the wire to their own endpoint. Because the shop domain is not part of the signed payload, the attacker can replay that exact `(body, hmac)` pair against the app's public webhook endpoint while setting the `shop-domain` header to any other merchant's `myshopify.com` domain. `Registry.process` will accept it (HMAC over body validates) and dispatch it to the app's handler tagged with the victim shop, `data.shop` in `WebhookMetadata`. If the host application uses `data.shop` to key writes to its own datastore (order/customer records, uninstall/redact handling, billing state, etc. — this is the intended usage pattern per `docs/usage/webhooks.md` and the `WebhookHandler` interface), this results in cross-tenant data injection or corruption: an attacker-controlled payload being attributed to and acted upon for a victim merchant's tenant, without ever needing the app's `client_secret`, any merchant's access token, or any credential belonging to the victim. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is significant for any app that exposes a public webhook endpoint (a documented, standard integration pattern for this gem) and relies on `data.shop` for tenant attribution without extra verification. The only precondition is the attacker being able to install the app on a shop they control — a normal, unprivileged action available to anyone — and capturing one legitimately delivered webhook to observe a valid `(body, hmac)` pair, then replaying it with a different `shop-domain` header.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the verified HMAC to the shop it was issued for. Concretely:
- Include the `shop-domain` header (and ideally `webhook-id`/timestamp for anti-replay) in `to_signable_string`, or
- After validating the body HMAC, independently verify that the shop in the header corresponds to a shop with a currently installed/active session for this app (reject shops with no known install), and
- Track `webhook_id` to reject replays/duplicates.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (an ordinary, unprivileged action).
2. App receives a legitimate Shopify webhook for a subscribed topic, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "<attacker-controlled content>"}
   ```
3. Attacker captures this exact `(body, hmac)` pair (observable to them since it was delivered to their own endpoint/logs).
4. Attacker resends the identical request to the app's public webhook endpoint, only changing the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(raw_body, api_secret_key)` — unchanged from step 2 — and it matches, so validation succeeds: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)`, and the host app processes attacker-controlled data under the victim's tenant identity.

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
