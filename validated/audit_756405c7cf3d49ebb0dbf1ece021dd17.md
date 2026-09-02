### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant dispatch without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` and `topic` values used to authorize, route, and attribute the webhook to a tenant are read from HTTP headers that are never included in the signed bytes. This breaks the intended binding `hmac_valid(secret) == (shop, topic, body)` down to `hmac_valid(secret) == (body)`, allowing an attacker who can obtain any single valid `(hmac, raw_body)` pair (e.g. from their own shop's legitimate webhook delivery) to replay it against the app's webhook endpoint with a forged `shop-domain`/`topic` header and still pass `HmacValidator.validate`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic linkage to that body: [2](#0-1) 

`Registry.process` validates the HMAC, then uses the unauthenticated `request.topic` to select the handler and forwards the unauthenticated `request.shop` straight into the data handed to the app's business logic: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. against the body string, never against `shop` or `topic`: [4](#0-3) 

Because the equality the library actually enforces is `HMAC(secret, raw_body) == received_hmac`, and NOT `HMAC(secret, raw_body ‖ shop ‖ topic) == received_hmac`, the `shop` value that ends up bound to the tenant-scoped `WebhookMetadata` passed to the host app's handler is not the value the secret actually vouches for — it is an attacker-controlled header. This is the same class of bug as the reported "two different `invariantCheck` variables" issue: the identity value that is checked (the HMAC over the body) is not the same identity value that is acted upon (the `shop`/`topic` headers used for dispatch and tenant attribution).

### Impact Explanation
Any party capable of obtaining one valid `(raw_body, hmac)` pair signed with the app's `api_secret_key` — trivially available to any merchant who installs the app on their own store and receives a single real webhook — can replay that exact body to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header and/or `shopify-topic` header. `HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` will dispatch the handler for the forged topic and hand it a `WebhookMetadata` claiming to be from an arbitrary victim shop. Depending on how the host application's handler trusts `data.shop` (e.g., to look up/update per-tenant records, credentials, or state), this enables cross-tenant data corruption or spoofed events attributed to a shop that never sent them — a cross-tenant boundary break carrying the app's own trust in Shopify's HMAC guarantee.

### Likelihood Explanation
Reachable by any unprivileged internet user who can install the app on any single shop (including a free/dev store) to harvest one legitimate `(body, hmac)` pair, then replay it directly to the app's internet-facing webhook endpoint with modified headers. No access token, `client_secret`, or privileged account is required — only observation of one legitimate webhook delivery, which is entirely attacker-controllable if they own any shop that installs the app.

### Recommendation
Bind `shop` and `topic` (and any other header-derived fields used for authorization/dispatch) into the signable string that is HMAC-verified, or otherwise cryptographically tie them to the verified body (e.g., include them as part of the canonical string passed to `to_signable_string`, matching the pattern already used in `AuthQuery#to_signable_string` where all identity-relevant fields are included). At minimum, document and enforce that host applications must independently verify `request.shop` against a known/registered shop list before trusting it, since the gem currently provides no cryptographic guarantee over that field.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture one legitimate webhook delivery, e.g. headers:
   ```
   shopify-topic: orders/create
   shopify-hmac-sha256: <valid-hmac-of-body>
   shopify-shop-domain: attacker.myshopify.com
   ```
   and raw body `{"id":1,...}`.
2. Replay the identical body and `shopify-hmac-sha256` value to the same webhook endpoint, but change:
   ```
   shopify-shop-domain: victim.myshopify.com
   shopify-topic: orders/create
   ```
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) still returns `true` because it only checks the HMAC of the raw body, per `lib/shopify_api/utils/hmac_validator.rb:12-31`.
4. The handler registered for `orders/create` receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker body>, ...)` (`lib/shopify_api/webhooks/registry.rb:198`), causing the host app to process attacker-supplied data as if it originated from `victim.myshopify.com`.

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
