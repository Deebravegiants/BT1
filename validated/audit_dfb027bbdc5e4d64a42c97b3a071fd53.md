### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unauthenticated headers while only the raw body is HMAC-covered - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` proves nothing about the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers. `Registry.process` nonetheless treats `request.shop`/`request.topic` as trusted identifiers when dispatching to the app's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `HmacValidator.validate` computes the HMAC exclusively over that signable string: [2](#0-1) 

so the signature only binds the raw body bytes to the shared `api_secret_key`; it never binds `shop`, `topic`, or `webhook_id`. Yet `Registry.process` uses those header-derived, unsigned fields as the authoritative identity for routing and for the data handed to the app's handler: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are all read straight from headers with no cross-check against the signed payload: [4](#0-3) 

The broken identity binding is: `hmac_valid(body) == true` is treated as equivalent to `shop_header == actual_originating_shop`, when in fact the HMAC only proves `hmac_valid(body, api_secret_key)`, independent of any header value.

Because Shopify apps use a single `api_secret_key` shared across every shop that installs the app, any shop that has installed the app (which any unprivileged internet user can do for a public app by installing it on their own store) can obtain a webhook whose body+HMAC pair is valid for that shared secret. That same `(raw_body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers rewritten to name a different, victim shop — `Utils::HmacValidator.validate(request)` still returns `true` since it only checks the body bytes, and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the victim shop/topic.

### Impact Explanation
This breaks the tenant boundary the gem's own webhook HMAC check is supposed to enforce: an attacker who legitimately installed the app on their own shop can forge webhook deliveries that `ShopifyAPI::Webhooks::Registry.process` will accept as authentic for an arbitrary victim shop and/or topic, because `shop`/`topic`/`webhook_id` are never covered by the signature. Any host application relying on this gem's `process` result to identify which shop/topic a webhook body belongs to (a documented, intended use per `docs/usage/webhooks.md`) can be made to apply attacker-controlled payload content to the wrong tenant's records — a cross-tenant integrity/confidentiality issue that flows directly from this gem's `to_signable_string`/`process` implementation rather than any misuse of the API.

### Likelihood Explanation
Requires only: (1) attacker installs the target app on their own store (available to any developer/merchant testing a public app, no special privilege), (2) attacker captures one legitimate webhook delivery to their own endpoint (trivial — this is literally the documented flow), (3) attacker replays the same raw body/HMAC to the target app's webhook route with modified `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id` headers. No secret, token, or victim credential is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body), and/or require the host app to validate `request.shop` against a known/installed shop's session before trusting handler data, since the current `to_signable_string` in `lib/shopify_api/webhooks/request.rb` intentionally excludes them.

### Proof of Concept
1. App is publicly installable; attacker installs it on `attacker-shop.myshopify.com` and registers for topic `customers/data_request` (or any topic).
2. Shopify delivers a webhook to the attacker's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: customers/data_request`, `x-shopify-hmac-sha256: <valid-hmac-of-raw-body>` and some `raw_body`.
3. Attacker POSTs the identical `raw_body` (and thus identical, still-valid HMAC) to the same app's webhook endpoint but with `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which returns `true` (only checks body bytes against secret), then invokes the handler with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` — the app now processes attacker-supplied content under the victim shop's identity.

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
