### Title
Webhook shop/topic identity spoofing via unauthenticated headers — HMAC only covers the raw body ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` authenticate a webhook delivery by validating an HMAC computed **only over the raw request body**, while the `shop` and `topic` values used to route and attribute the webhook are read from unauthenticated HTTP headers that are never included in the signed material. This breaks the identity binding `shop_used_by_handler == shop_authenticated_by_HMAC`.

### Finding Description
`Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

and `Request#shop` / `Request#topic` are pulled straight from headers with no cryptographic tie to that body: [2](#0-1) 

`HmacValidator.validate` verifies `hmac` against `to_signable_string` (the body) alone: [3](#0-2) 

`Registry.process` then trusts `request.shop` and `request.topic` for tenant/handler dispatch after only confirming the body's HMAC is valid: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, the app's client secret) is identical across **every shop** that has installed the same public app, any merchant who has installed the app receives their own genuine, validly-signed webhooks. That merchant can capture a real `(raw_body, hmac)` pair delivered to their own store and replay it to the app's webhook endpoint while rewriting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a *different* shop that also uses the app. `HmacValidator.validate` still succeeds because it only checks the untouched body bytes against the shared secret — it never binds the signature to the shop or topic headers. `Registry.process` will then invoke the app's handler with `WebhookMetadata#shop` set to the victim shop and attacker-controlled body content, causing the host application to attribute forged webhook data to a tenant the attacker does not own.

This is exactly the "field acted on but not covered by the HMAC" pattern: the equality that should hold — `shop_authenticated == shop_used_by_handler` — does not, since `shop` is parsed from an unauthenticated header while only the body is authenticated.

### Impact Explanation
Any shop with the app installed can forge webhook events that are attributed to another tenant's `shop` (and/or a different `topic`), causing the host application to write/update state, trigger business logic, or fulfil actions for a shop it does not control. This is a cross-tenant access primitive delivered entirely through this gem's webhook verification API (`HmacValidator.validate` / `Webhooks::Registry.process`), requiring no access token, secret, or privileged account beyond that of any regular installed merchant.

### Likelihood Explanation
Any merchant that installs the app already receives real, validly-signed webhook deliveries for their own store, giving them a ready-made `(body, hmac)` pair. Forging the request only requires changing plaintext HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`) — no cryptography needs to be broken, no secret needs to be recovered. This can be done by any unprivileged Shopify merchant capable of installing the target public app.

### Recommendation
Bind the `shop` (and ideally `topic`) to the authenticated payload instead of trusting them from headers alone:
- Include `shop`, `topic`, and `webhook-id` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body), so `HmacValidator.validate` fails if any of these are altered.
- Alternatively/additionally, cross-check `request.shop` against an already-authenticated session/shop record known to the host app (e.g., that the shop has a stored session/access token) before dispatching to a handler, rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com`.
2. Shopify delivers a genuine webhook (e.g., `orders/create`) to the app:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - Body: `{"id": 123, ...}`
3. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. In `Webhooks::Request.new`, `shop` becomes `"victim-shop.myshopify.com"` [5](#0-4) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the shared `api_secret_key` [6](#0-5) .
6. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ...)` [7](#0-6) , causing the host app to process attacker-supplied data as if it originated from `victim-shop.myshopify.com`.

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
