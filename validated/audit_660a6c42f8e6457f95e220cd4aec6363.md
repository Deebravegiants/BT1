### Title
Webhook `shop` and `topic` identity is trusted from unauthenticated headers while the HMAC signs only the raw body, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the payload bytes but never binds the `shopify-shop-domain` or `shopify-topic` headers to that signature. `Registry.process` then dispatches the handler using `request.shop` and `request.topic` taken directly from those unauthenticated headers, so a captured genuine webhook (valid body + valid HMAC) can be replayed with forged shop/topic headers and still pass validation.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, bytes_that_determine_tenant_and_topic)`. Instead the gem verifies:

`hmac == HMAC(secret, raw_body)` while `shop = header("shopify-shop-domain")` and `topic = header("shopify-topic")` are read independently and never included in the signed material. [1](#0-0) [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) 

`Registry.process` then trusts the unauthenticated `shop` field and hands it straight to the app's handler as tenant identity: [4](#0-3) 

Because a single app-level `api_secret_key` (client secret) signs webhooks for every shop that installs the app, any merchant who installs the app on their own store receives genuine `(raw_body, hmac)` pairs signed with that shared secret for their own events. That same merchant can capture such a pair and POST it to the app's webhook endpoint again, this time substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a different, victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the untouched body bytes against the untouched HMAC; the header substitution is invisible to the signature check. `Registry.process` then invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the app to record/act on data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant/topic binding that webhook consumers rely on to route data per-shop. An attacker (any unprivileged merchant who has installed the app, i.e., an ordinary internet-facing user of a multi-tenant app, not the app owner) can inject attacker-controlled webhook payloads under an arbitrary victim shop's identity/topic, without ever possessing `api_secret_key`. Depending on how the hosting app persists webhook data (order records, inventory updates, GDPR/mandatory-topic handling, etc.), this enables cross-tenant data pollution or spoofed events attributed to a shop the attacker does not control — satisfying the "cross-tenant access" High-impact category.

### Likelihood Explanation
Any app built on this gem that serves more than one shop (the normal, documented multi-tenant use case in `docs/usage/webhooks.md`) is affected. The only prerequisite is that the attacker legitimately installs the app on one shop (no special privilege) and can capture one of their own genuine webhook deliveries (trivial, since it is sent to their own configured endpoint or can be intercepted/logged by the attacker's own infrastructure), then replay it with modified headers to the same public endpoint.

### Recommendation
Include the `shopify-shop-domain` (and ideally `shopify-topic`, `shopify-webhook-id`) values in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the request (e.g., verify that `shop` matches a shop that currently has an active session/webhook subscription in the app's own storage, and additionally reject replays via `webhook-id` uniqueness/idempotency tracking). At minimum, document that `request.shop`/`request.topic` are unauthenticated and must be independently cross-checked by the host application against known installed shops before use.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com`, both webhooks signed with the same app `api_secret_key`.
2. Attacker triggers/receives a legitimate webhook for their own shop, capturing `raw_body` and the valid `shopify-hmac-sha256` header.
3. Attacker POSTs the same `raw_body` and `hmac` to the app's webhook endpoint, but sets:
   `shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers; `HmacValidator.validate` succeeds because it only checks `raw_body` against the (untouched) HMAC.
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, causing the application to process attacker-controlled data under the victim shop's tenant identity.

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
