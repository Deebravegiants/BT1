Confirmed. `WebhookMetadata.shop` and `topic` are passed directly to every registered `WebhookHandler#handle` implementation, and the only integrity check performed before dispatch is `Utils::HmacValidator.validate(request)`, which signs/verifies `request.to_signable_string` — i.e., the raw body only.

### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw HTTP body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` only verifies the HMAC over that body before dispatching the handler with the header-derived `shop` [3](#0-2) .

### Finding Description
The HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has installed the app [4](#0-3) . Any merchant who installs the app can register a webhook subscription pointing at an endpoint they control (e.g., a request-capture tool) and thereby obtain a legitimately-signed `(body, hmac)` pair — this pair is valid under the exact same secret used to sign webhooks for every other tenant of the app.

Because `HmacValidator.validate` only checks `to_signable_string` (the raw body) against the HMAC [5](#0-4) , an attacker can take that captured, validly-signed `(body, hmac)` pair and replay it directly to the target app's real webhook endpoint while freely substituting the `shopify-shop-domain` (and `shopify-topic`) headers to any value of their choosing. `Request#shop` and `Request#topic` are read straight from those attacker-controlled headers with no cryptographic binding to the signed body [6](#0-5) , so `Registry.process` will accept the forged request, route it to the correct topic handler, and hand the handler a `WebhookMetadata` whose `shop` field is entirely attacker-controlled [7](#0-6) , [8](#0-7) .

This breaks the identity binding `shop authenticated == shop used by handler`: the byte range verified by the HMAC (body only) does not equal the byte range trusted by the application (headers, via `data.shop`). Any host application whose `WebhookHandler#handle` implementation keys business logic (session lookup, data deletion, state changes, GraphQL calls using the stored access token for that shop) off `data.shop` can be made to act on behalf of an arbitrary victim shop, using only a webhook payload the attacker fully authored for their own shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who is a legitimate but unprivileged customer of the app (installed on their own shop) can cause the app to process attacker-authored webhook payloads under the identity of any other shop using the app, with no need for that victim shop's credentials. Depending on the host app's handler logic (e.g. `app/uninstalled`, `shop/redact`, order/customer mutation handlers), this can lead to unauthorized state changes, data deletion, or actions performed against a victim tenant's stored session/access token — i.e., cross-tenant access.

### Likelihood Explanation
Any developer/merchant with the app installed can trivially self-issue a genuine `(body, hmac)` pair by pointing a webhook subscription at a capture endpoint, then replay it with a forged `shop`/`topic` header set to any target app's webhook receiver. No secret material beyond normal app usage is required, making this straightforward for any registered user of the app to exploit.

### Recommendation
Bind the trusted identity fields into the signed material, or independently authenticate them: e.g. include `shop`, `topic`, and `webhook_id` inside the HMAC-covered payload (or verify them against the delivery address / a per-shop secret / a separate Shopify-signed claim) rather than trusting `shopify-shop-domain` and `shopify-topic` headers as bare, unauthenticated input in `Request#shop` / `Request#topic`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook subscription (any topic) pointing to an HTTP-capture endpoint they control.
2. Shopify delivers a genuinely-signed webhook: headers `x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, plus a body the attacker can partly influence (e.g., via the resource they create/update to trigger the webhook).
3. Attacker replays the exact same body + `x-shopify-hmac-sha256` value to the target app's real webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
4. `HmacValidator.validate` recomputes the HMAC over the body only [9](#0-8)  — it matches, because the body and secret are unchanged.
5. `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` [3](#0-2) , causing the host app to execute tenant-scoped logic under the victim's identity using attacker-controlled body content.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-15)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
