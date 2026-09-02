Confirmed: the webhook HMAC only signs `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to that signature [2](#0-1) . This is enough to complete the analysis.

### Title
Webhook shop-domain / topic identity spoofing via HMAC that only covers the request body, not headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from the `x-shopify-*` HTTP headers, but `Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string`, which is defined as the raw request body alone. The identity fields that `Webhooks::Registry.process` hands to app handlers are therefore never covered by the signature that is supposed to authenticate the webhook's origin.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)` [3](#0-2) . `HmacValidator.validate` recomputes an HMAC-SHA256 over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly from headers with no relation to the signed bytes [2](#0-1) .

This breaks the identity binding: `bytes verified == raw_body` but `bytes acted on (shop, topic) != bytes verified`. Once a valid `(raw_body, hmac)` pair is obtained for one shop's webhook (a merchant can legitimately request their own store to fire a webhook to an endpoint they control, or capture a delivery to any endpoint they operate), it can be replayed with the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers rewritten to any value — the signature check still passes because those headers are never part of the signed content. `Registry.process` then dispatches to the app's registered handler with the attacker-chosen `shop` and `topic` in `WebhookMetadata`, which the host app is expected to trust as the authenticated identity of the event [5](#0-4) . Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly includes `shop` in the signed parameter set [6](#0-5) , showing that the OAuth path binds `shop` to its HMAC while the webhook path does not.

### Impact Explanation
An attacker who owns or controls any store (or any endpoint that legitimately receives a real webhook delivery) can capture a genuine `(body, hmac)` pair and replay it against the same app's webhook endpoint while forging the `shop-domain` header to name a different, victim shop, and/or forging `topic`/`webhook-id`. Because `HmacValidator.validate` only checks the body signature, the forged request passes validation and is routed to the handler as if it were an authenticated event for the victim shop. Any app logic that keys off `WebhookMetadata#shop` (e.g., to look up a session/access token, update per-shop state, or process an `app/uninstalled` or `shop/redact` event for what it believes is the victim's tenant) is fed attacker-controlled tenant identity, producing cross-tenant data corruption/confusion — a boundary violation between one merchant's authenticated identity and another's.

### Likelihood Explanation
Exploitation requires no secret material: the attacker never needs `api_secret_key`. They only need one legitimate webhook delivery (from their own shop, trivially obtainable by installing the app or triggering any webhook-eligible event on a store they control) and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint. The header rewrite is trivial and the vulnerable code path (`Registry.process` → `HmacValidator.validate` → `Request#to_signable_string`) is exercised on every inbound webhook.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the signed content checked by `HmacValidator`, or independently verify that the `shop` header corresponds to a shop with a session/installation known to the app before trusting it, rather than relying on the raw-body-only HMAC to authenticate those header-derived fields.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers a webhook-eligible event, capturing the exact `raw_body` and `x-shopify-hmac-sha256` header the app receives (this pair is valid because the app's own installed store generated it).
2. Attacker replays a POST to the app's webhook endpoint using the *same* `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: shop/redact` (or any topic the attacker wants processed).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(raw_body)` — unaffected by the header changes.
4. The app's registered handler for that topic is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "shop/redact", body: <attacker's original body>, ...)`, causing the app to act on victim-shop identity using attacker-supplied body content.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
