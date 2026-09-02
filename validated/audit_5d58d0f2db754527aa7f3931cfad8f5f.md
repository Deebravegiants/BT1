### Title
Webhook `shop-domain` header trusted for tenant identity without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once `Utils::HmacValidator.validate(request)` passes, but the HMAC only ever signs the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values that the gem hands to the application's handler as trusted tenant/routing metadata are read straight from HTTP headers that are never part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read from headers, independent of the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop`, `request.topic`, etc. to build `WebhookMetadata` passed to the application's handler as the identity context for the event: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` only (i.e., the raw body for webhook requests), never the headers: [4](#0-3) 

This breaks the identity binding: `hmac_valid == true` should imply `(body, shop, topic) == (body, shop, topic) as sent by Shopify`, but in practice `hmac_valid` only proves `body == body as sent by Shopify`. The `shop` (tenant) header is decoupled from the authenticated bytes.

Because the webhook endpoint is a public HTTP endpoint (any internet-reachable POST target the host app exposes per the gem's documented usage), an unprivileged party who is themselves a legitimate merchant/tenant of the app can capture one of their own authentic webhook deliveries (raw body + valid `x-shopify-hmac-sha256`), then replay the identical body/HMAC pair while substituting the `x-shopify-shop-domain` header for a different (victim) shop. `Utils::HmacValidator.validate` still returns `true` because it never inspected the header, and `Registry.process` forwards `shop: request.shop` (the attacker-supplied header value) to the handler as if it were an authenticated fact.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to select which tenant's records to update/delete/create (the intended and documented use of webhook processing), an attacker can cause webhook-driven side effects to be attributed to, or applied against, a shop they do not own — i.e., cross-tenant data manipulation using only their own legitimate app installation's webhook traffic as raw material. This matches the "cross-tenant access" high/critical impact category: no credentials, TLS interception, or privileged access are required, only the ability to receive one legitimate webhook for one's own shop and replay it with a modified header against the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is high for any application that relies on `ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata#shop` as the sole tenant-identifying signal (which is exactly what the gem's API surfaces and encourages). Any merchant with the app installed can generate a legitimate signed body for their own shop, then resend it with a different `x-shopify-shop-domain` header value to the app's public webhook callback route.

### Recommendation
- Document/enforce that `request.shop` from `ShopifyAPI::Webhooks::Request` is **not** cryptographically bound and must not be trusted as tenant identity on its own.
- Where possible, cross-check the header-derived `shop` against a shop identity that is otherwise authenticated (e.g., verify the webhook was expected/registered for that specific shop, or correlate against an existing session/store record) before applying any mutating action.
- Consider extending `to_signable_string` (or a companion check) to include the header-derived `shop`/`topic` in a bound comparison against the app's known webhook registrations, so `HmacValidator.validate` failure implies a genuine mismatch, not just body tampering.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal, low-privilege merchant install) and lets a normal webhook (e.g. `orders/create`) fire, capturing the exact raw POST body and its `x-shopify-hmac-sha256` header sent by Shopify to the app's registered webhook URL.
2. Attacker POSTs the exact same body + HMAC header to the same webhook endpoint again, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. In `ShopifyAPI::Webhooks::Registry.process`, `Utils::HmacValidator.validate(request)` returns `true` (line `lib/shopify_api/webhooks/registry.rb:190`) because it only checks the raw body against the app's own `Context.api_secret_key`, which is unaffected by the header change.
4. `request.shop` (`lib/shopify_api/webhooks/request.rb:21-23`) now returns `"victim-shop.myshopify.com"`, and this value is passed into `WebhookMetadata` given to the application's registered handler as authoritative shop context (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the actual signed event data originated from the attacker's own shop.

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
