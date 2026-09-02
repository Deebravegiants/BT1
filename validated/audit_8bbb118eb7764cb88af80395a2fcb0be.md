### Title
Webhook `shop-domain` and `topic` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` only validates the HMAC of the body via `HmacValidator.validate`, then dispatches the handler using the header-derived `shop`/`topic`/`webhook_id` values without binding them to the signature. Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any shop that legitimately receives one webhook can replay that exact `(body, hmac)` pair while swapping the `shop-domain`/`topic` headers to impersonate a different shop.

### Finding Description
The signable string used for HMAC verification is defined as: [1](#0-0) 

But `shop`, `topic`, and `webhook_id`, which are trusted and passed on to the handler, come only from headers: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then trusts the header-derived identity fields when invoking the handler: [3](#0-2) 

The HMAC key is the app's `client_secret` (`Context.api_secret_key`), which is identical for every merchant/shop that has installed the app — it is not shop-specific: [4](#0-3) 

Since the signature only binds the body bytes, and the key is shared across tenants, the equality the code relies on — "the shop whose secret produced this valid signature" == "`request.shop` passed to the handler" — does not hold. Any shop can capture a legitimate webhook delivered to their own endpoint (a valid `(raw_body, hmac-sha256)` pair signed with the shared app secret) and resend it to the app's webhook endpoint with the `shopify-shop-domain` (and/or `shopify-topic`) header changed to another shop's domain. `HmacValidator.validate` will still pass because it never inspects those headers, so `Registry.process` calls the handler with attacker-chosen `shop`/`topic` while the HMAC only proves "some installer of this app produced this body," not "this specific shop produced this body under this topic."

### Impact Explanation
This breaks the tenant/shop identity binding for the only cryptographic check webhook processing performs, permitting cross-tenant data injection or corruption: an attacker-controlled shop can trick the host application's webhook handler into applying data (or destructive events, e.g. `app/uninstalled`, `shop/redact`, `orders/create`) as if it originated from a victim shop it does not control. Per the report's impact taxonomy this is Critical — cross-tenant access — since the gem's own verification primitive fails to bind the identity field it exposes to callers.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate installer of the target app (an "unprivileged" tenant relative to other merchants) capable of receiving at least one real webhook for their own shop — no access token, `api_secret_key`, or privileged account is needed. Capturing a `(raw_body, hmac)` pair from one's own inbox and replaying it with modified headers against the app's public webhook endpoint is a single HTTP request.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signable string (or otherwise cryptographically authenticate them), so `HmacValidator.validate` fails if any identity header is altered. At minimum, document/require that host applications independently verify the `shop` header corresponds to an installed session before trusting `WebhookMetadata#shop`, but the safer fix is inside `Webhooks::Request#to_signable_string` in this gem.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (same `client_secret`).
2. Attacker controls `shop-a` and receives a real webhook: headers `shopify-shop-domain: shop-a.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid-for-body>`, plus `raw_body`.
3. Attacker resends the same `raw_body` and `hmac-sha256` to the app's webhook endpoint but sets `shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (`@raw_body`) against the shared secret — see [5](#0-4) .
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: ...)` and processes/updates data as if it came from `shop-b`, even though `shop-b` never sent it.

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
