### Title
Webhook `shop` (and `topic`) header not covered by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while `shop`, `topic`, and `webhook_id` are taken directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then unconditionally trusts these header-derived fields when dispatching to the app's webhook handler, breaking the binding "shop that produced the signed bytes == shop the app attributes the event to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `#topic`, `#webhook_id`) are read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks that `hmac` matches `HMAC(api_secret_key, to_signable_string)` — i.e. it verifies the body bytes, not the shop: [3](#0-2) 

`Registry.process` performs exactly this check and then builds `WebhookMetadata` straight from the unauthenticated `request.shop`/`request.topic`, handing it to the app's handler as if it were verified: [4](#0-3) 

Because the HMAC secret (`api_secret_key`) is shared across every shop installed on a given app (it's not per-shop), an attacker who controls their own Shopify store can install the target app, trigger a real webhook for their own shop, and obtain a body + HMAC pair that legitimately validates under the app's `api_secret_key`. The attacker can then resend that exact validated `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain (and/or `shopify-topic`). `Utils::HmacValidator.validate` still returns `true` (it only checks the raw body), so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain, tenant-binding equality broken:

`HMAC-authenticated shop == shop attributed to webhook data` is false; the actual equality enforced is only `HMAC-authenticated raw_body == raw_body`, while `shop` is asserted (parsed) but never verified.

### Impact Explanation
This lets an unprivileged internet user (any developer who can install the app on a throwaway/dev store) forge webhook events that the host application will attribute to an arbitrary victim shop domain, without ever needing the victim's credentials, access token, or the app's `client_secret`. Depending on how the host app persists/acts on webhook data keyed by `data.shop` (e.g. updating shop-scoped records, uninstall/GDPR handling, order/customer data ingestion), this results in cross-tenant data injection/corruption — matching the "cross-tenant access" Critical-impact category, since the attacker's controlled payload is processed under a foreign tenant's identity.

### Likelihood Explanation
Moderate-to-high likelihood: the attack requires only (1) installing the app on any shop the attacker controls (many apps offer free/dev-store installs), (2) triggering any webhook topic the app subscribes to, and (3) replaying the intercepted body/HMAC with a modified `shop` header to the app's public webhook endpoint. No secret material or victim interaction is needed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable string, or otherwise cryptographically tie the header value to the payload before trusting it — e.g. include these headers as part of `to_signable_string`, or require the host app to independently confirm that `shop` corresponds to a known, previously-installed session before acting on the payload. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must be independently validated by the consuming application (e.g. checked against a session store) before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (a store they control) and lets the app register a webhook, e.g. `orders/create`.
2. Attacker triggers the webhook (e.g., creates a test order), capturing the raw POST body `B` and its valid header `x-shopify-hmac-sha256` computed by Shopify using the app's `api_secret_key`.
3. Attacker resends an HTTP request to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim.myshopify.com` and optionally forges `x-shopify-topic`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` (`Request#to_signable_string`), which is unchanged.
5. The registry looks up the handler for the (possibly attacker-chosen) topic and invokes it with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-authored data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
