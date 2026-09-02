### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery via replay - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, and `webhook_id` values that are handed to the app's handler come from HTTP headers that are never included in the signed payload. An attacker who is able to obtain any single legitimately-signed `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and receiving one real webhook) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header for a victim shop, and the gem will accept it as authentic and dispatch it to the merchant's webhook handler as if it came from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read straight from HTTP headers, independent of the signed content: [2](#0-1) 

`Registry.process` validates authenticity purely via `Utils::HmacValidator.validate(request)` (which in turn calls `to_signable_string`, i.e., only the body), then builds `WebhookMetadata` directly from the unauthenticated header-derived `shop`/`topic`/`webhook_id` and dispatches it to the registered handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body) using the app's `Context.api_secret_key`, and only compares that digest — it has no visibility into or binding to the `shop-domain` header: [4](#0-3) 

**Broken binding (equality that should hold but doesn't):**
`hmac_valid_for(raw_body) ⇒ shop_header == shop_that_actually_sent(raw_body)`

In reality the check only proves `hmac_valid_for(raw_body)`; it says nothing about which shop the body came from, because `shop-domain` is not part of the signed string. Since Shopify signs the webhook body with the **app's** `client_secret` (the same secret for every shop that installs the app), an unprivileged user who installs the same public app on their own store receives valid `(raw_body, hmac)` pairs signed with that same shared secret. They can then send that exact body+HMAC to the app's webhook endpoint while setting `x-shopify-shop-domain` (or `shopify-shop-domain`) to an arbitrary victim shop domain string, and `Registry.process` will accept it and invoke the handler with `shop: <attacker-chosen victim domain>`.

### Impact Explanation
This crosses the tenant boundary the gem is meant to preserve: it lets one merchant (the attacker, who is a legitimate but unprivileged installer of the same app) inject data attributed to an arbitrary other shop domain into the app's webhook processing pipeline (e.g., `orders/create`, `customers/data_request`, or any subscribed topic), without needing the victim's access token, the app's `client_secret`, or any privileged access — only their own valid installation. Depending on how the host application uses `WebhookMetadata#shop` (commonly to look up/create per-shop records, trigger per-shop side effects, or key data storage), this enables cross-tenant data poisoning/confusion, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only: (1) becoming an installer of the target app (trivial — any developer/merchant can install a public app on a free dev store), (2) capturing one legitimately delivered webhook body+HMAC destined for their own store, and (3) resending it to the app's public webhook endpoint with a forged `shop-domain` header. No credentials, secrets, or privileged access to the victim account are needed, and the header manipulation is standard HTTP request tampering, making this readily reachable by any unprivileged internet user who has installed the app once.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the signed payload rather than trusting the raw headers independently of the HMAC:
- Verify that `request.shop` matches the shop associated with the session/webhook subscription the app expects for that specific webhook delivery (e.g., cross-check against known installed shop domains before dispatch), and/or
- Include the `shop-domain` and `topic` headers as part of the string that is HMAC-validated (matching what Shopify signs), rather than relying on `to_signable_string` returning only the raw body.
- At minimum, document that `shop`/`topic` are not authenticated by the HMAC and that host applications must independently verify the shop is one they actually registered this specific webhook subscription for before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker-shop.myshopify.com` and receives a real webhook delivery, capturing the raw request body `B` and its header `x-shopify-hmac-sha256: H` (valid because it's signed with the app's shared `client_secret`).
2. Attacker sends a forged HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid for `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - Header `x-shopify-topic:` unchanged or same topic
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B`: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the body/data actually originated from the attacker's own shop, breaking the shop-identity binding.

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
