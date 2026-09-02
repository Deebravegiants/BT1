### Title
Webhook HMAC Covers Only the Raw Body, Not the `shop-domain`/`topic`/`webhook-id` Headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers and are never included in the HMAC-signed material. `Registry.process` trusts `request.shop` and `request.topic` to route the payload to a handler and to build `WebhookMetadata`, creating a binding mismatch: the byte string that is HMAC-verified (`body`) is not the byte string that is actually acted upon (`body` + `shop` + `topic` + `webhook_id`).

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that are completely outside the signed payload: [3](#0-2) 

`Registry.process` then dispatches based on these unauthenticated header fields: [4](#0-3) 

Because only the body bytes are covered by the HMAC, the equality the code should enforce — `hmac == HMAC(secret, body ++ shop ++ topic ++ webhook_id)` — is broken down to `hmac == HMAC(secret, body)`. Any request carrying a `(body, hmac)` pair that once validated for one shop/topic (e.g. captured from a legitimate webhook delivery, a webhook the attacker's own store received, or a topic/shop combination whose body happens to match) will pass HMAC validation for **any** `shop-domain`/`topic`/`webhook-id`/`api-version` header value the requester supplies, since these are never part of the signed string.

### Impact Explanation
This breaks the identity binding between the cryptographically verified bytes and the tenant/topic the application acts on. An attacker who can supply a valid `(raw_body, hmac)` pair for their own shop (which they legitimately receive since they can install the app on their own store) can replay that exact body+hmac while forging the `x-shopify-shop-domain` header (or `shopify-shop-domain` in the new format) to claim it belongs to a **different**, victim shop, and forge `x-shopify-topic`/`webhook-id` to claim a different topic. `Registry.process` will treat the request as "HMAC verified" and hand the attacker-chosen `shop` and `topic` to the registered handler via `WebhookMetadata`, potentially causing the host application to apply order/customer/product data intended for one merchant to another merchant's tenant records — a cross-tenant data integrity/confusion issue, matching the "field acted on but not covered by the HMAC" bug class from the report.

### Likelihood Explanation
Exploitation only requires the ability to send an HTTP POST to the app's public webhook endpoint with attacker-controlled headers — something any unprivileged internet user (or any merchant who has installed the app and thus legitimately receives at least one signed body) can do without possessing `api_secret_key`, an access token, or any other credential. The severity is bounded by the fact that the attacker must supply a body whose HMAC they already know (i.e., previously observed for their own or any shop's valid webhook), so it is not a full signature forgery — but it is a genuine authentication/binding weakness because the header fields the application logic relies on for tenant/topic routing are never verified.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (and ideally `api_version`) in the string that is HMAC-verified, or otherwise cryptographically bind these header values to the signed body (e.g., by having the host application independently confirm the `shop-domain` header against its own session store before trusting `WebhookMetadata#shop`). At minimum, document prominently that `Registry.process`'s HMAC check does not authenticate the `shop`, `topic`, or `webhook_id` headers, so consuming applications must not treat a passing `HmacValidator.validate` as proof of which shop or topic a webhook is for.

### Proof of Concept
1. Register a webhook handler for `orders/create` in the host app using `ShopifyAPI::Webhooks::Registry.add_registration`.
2. Attacker installs the app on their own store (`attacker-shop.myshopify.com`) and receives a legitimate webhook, capturing its raw body `B` and valid `hmac-sha256` header `H` (computed by Shopify over `B` with the shared secret).
3. Attacker POSTs to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256`: `H` (unchanged, still validates because `to_signable_string` only returns `B`)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - `x-shopify-topic`: `orders/create` (unchanged or forged to another registered topic)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the host application to process attacker-supplied order data as if it belonged to `victim-shop.myshopify.com`.

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
