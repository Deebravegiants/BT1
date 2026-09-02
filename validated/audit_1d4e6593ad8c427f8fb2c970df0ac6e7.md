This confirms the vulnerability. `Registry.process` at `lib/shopify_api/webhooks/registry.rb:188-200` only validates `Utils::HmacValidator.validate(request)`, which relies on `Request#to_signable_string` returning only `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`), never incorporating `shop`. The `shop` value passed into the handler comes straight from an attacker-controlled header (`shopify-shop-domain`/`x-shopify-shop-domain`) via `Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`), so it is never bound by the HMAC that gates `process`.

### Title
Webhook `shop` identity is not bound by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw body via `Utils::HmacValidator.validate(request)`. The `shop` identity that is subsequently handed to the app's `WebhookHandler` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed payload. Because the app's `client_secret` (`Context.api_secret_key`) is shared across every shop that has installed the app, any merchant who has installed the app can capture one legitimate webhook delivery to their own endpoint (with a valid body+HMAC pair) and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a different, victim shop. The signature still validates because it never covered `shop` in the first place.

### Finding Description
- `Registry.process` gates handling entirely on the HMAC check: [1](#0-0) 
- `Utils::HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string`: [2](#0-1) 
- For webhook `Request` objects, `to_signable_string` returns only the raw body — `shop`, `topic`, and `webhook_id` are excluded from the signable material: [3](#0-2) 
- The unauthenticated `shop` value is then trusted as the tenant identity passed to the handler: [4](#0-3) 

The identity binding that should hold is: `shop used by handler == shop cryptographically bound to the signed payload`. Here it instead holds only `hmac(body) == hmac(body)`, with `shop` fully attacker-controlled independent of the signature. Since the secret is per-app (not per-shop), any shop installed on the app can produce a valid `(body, hmac)` pair and freely relabel it as coming from any other shop.

### Impact Explanation
This breaks the tenant/shop authentication boundary the gem is expected to enforce for webhook processing: a malicious merchant who has installed the app can make the host application believe attacker-supplied webhook data originated from an arbitrary victim shop (cross-tenant confusion). Any host logic that keys off `WebhookMetadata#shop` (e.g., to look up per-shop data, sessions, or trigger per-shop actions) can be manipulated with forged tenant identity while still passing this gem's signature check.

### Likelihood Explanation
Requires only that the attacker be an unprivileged but legitimate installer of the target app (no special privileges, no access to `client_secret` or tokens) — they simply capture their own valid webhook delivery and resend it with an altered shop header to the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the signable string used for HMAC verification, or independently verify that the `shop-domain` header corresponds to the shop identity actually associated with the request before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; wait for (or trigger) a legitimate webhook delivery to the app's endpoint, capturing `raw_body` and the resulting valid `shopify-hmac-sha256` value.
2. Replay an HTTP POST to the same app webhook endpoint with the identical `raw_body`/`hmac` but with `shopify-shop-domain` set to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — [5](#0-4)  — which passes because it only checks the body's HMAC.
4. The handler is invoked with `shop: request.shop` == `victim.myshopify.com`, even though the payload never came from Shopify on behalf of that shop — [4](#0-3) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
