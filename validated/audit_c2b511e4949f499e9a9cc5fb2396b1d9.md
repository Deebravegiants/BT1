Investigating this, I found a genuine identity-binding gap that matches the report's underlying bug class ("a value used for security-relevant decisions but not covered by the value that was actually verified") — but in webhook processing, not in a runtime/bucket calculation (which doesn't exist in this Ruby gem).

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) used to attribute and dispatch the webhook come from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity handed to the app's handler — but that field was never part of what the HMAC actually verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are read straight from HTTP headers that are not part of the signed content: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body) and compare against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` checks the HMAC and, on success, immediately trusts `request.shop` as the merchant identity passed into the app's webhook handler: [4](#0-3) 

The binding that should hold is:
`hmac-sha256(secret, raw_body) == received_hmac` **and** `shop-domain header is bound to raw_body`

But what's actually implemented is only:
`hmac-sha256(secret, raw_body) == received_hmac`

The `shop-domain` header is completely decoupled from the signed payload. Since `api_secret_key` is a single per-app secret (not per-shop), any shop that installs the app can generate a validly-HMAC-signed webhook body for itself (e.g., by triggering an `orders/create` event on its own store), capture that `(raw_body, hmac)` pair, and replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a different, victim shop that also uses the same app. `Registry.process` will validate successfully (the HMAC only checks the body) and hand the attacker-controlled body to the handler tagged as belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an unprivileged user (any merchant who installs the public app on their own store) can inject attacker-chosen webhook payloads that the host application will process as if they originated from an arbitrary victim shop of their choosing. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., to look up the merchant's stored session/access token and perform actions, or write data keyed by shop), this enables cross-tenant data injection/confusion using only the identity binding flaw in this gem's own `Request`/`Registry` code — matching the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Likelihood is realistic but requires two conditions that are both attacker-reachable without special privileges: (1) the attacker must be able to install the target app on their own shop (trivial for public apps) to obtain one legitimately-signed `(body, hmac)` pair, and (2) the host app's webhook endpoint must be reachable and not perform its own additional shop-vs-installation binding check beyond what `shopify_api` provides. Because `shopify_api`'s own `Registry.process` does not perform this check itself and documents `shop` as trustworthy webhook metadata, apps relying solely on the gem's validation are exposed.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook_id`) header values in the HMAC-verified content, or otherwise cryptographically bind the shop identity to the signed body before exposing `request.shop` to handlers. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated relative to the HMAC and that hosts must independently verify the shop is one that has a valid session/installation before trusting it.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (any developer/free shop).
2. Attacker triggers a benign webhook (e.g., `orders/create`) on their own shop and captures the legitimate request: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because it's `HMAC(api_secret_key, B)`).
3. Attacker resends this exact request to the app's webhook endpoint, keeping body `B` and hmac header `H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`, which is unaffected by the header change: [4](#0-3) 
5. The app's `WebhookHandler.handle` is invoked with `data.shop == "victim-shop.myshopify.com"` and `data.body == B` (attacker-controlled), even though `victim-shop` never sent this webhook.

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
