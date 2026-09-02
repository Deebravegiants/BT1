### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` (parsed from the `x-shopify-shop-domain`/`shopify-shop-domain` header) as trusted tenant-identifying data, but `to_signable_string` — the value the HMAC is actually computed over — only covers the raw request body. `Registry.process` verifies the HMAC and then forwards the unauthenticated `shop` header straight to the app's webhook handler.

### Finding Description
`Webhooks::Request` includes `Utils::VerifiableQuery` and implements: [1](#0-0) 
which returns only `@raw_body`. The `shop` accessor is derived independently from a header and is never mixed into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then constructs `WebhookMetadata` using the unauthenticated `request.shop`, handing it to the registered handler as the tenant identity for this event: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the HMAC, never the shop header: [4](#0-3) 

This is the same bug class as the report: the code (and the downstream host application relying on this gem's `WebhookMetadata.shop`) implicitly assumes the HMAC-verified request also authenticates the shop-domain header, when in fact the HMAC binds only the body bytes. The identity binding that should hold — "verified bytes == bytes acted on for tenant attribution" — is broken because `shop` is bytes that are parsed but never verified.

### Impact Explanation
Because the app's client secret is shared across every shop that has installed the app (it is not shop-specific), any unprivileged internet user who installs the app on their own shop can legitimately trigger webhook deliveries (e.g. creating an order/product) and thereby obtain a genuine `(raw_body, hmac)` pair signed by Shopify. That attacker can then POST the exact same body and HMAC to the app's public webhook endpoint while substituting an arbitrary victim shop's domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` will pass (it only checks the body), and `Registry.process` will dispatch the event to the handler with `shop` set to the victim's domain. If the host application uses `WebhookMetadata#shop` to key per-tenant storage/state updates (the intended and documented use), this allows cross-tenant data confusion/corruption attributed to a shop the attacker does not control — meeting the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Reachable by any internet user who can install the app on a shop they control (a normal, unprivileged action) and who can send arbitrary HTTP requests to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is required. The only difficulty is that webhook *body content* is limited to what the attacker's own shop naturally generates (real events on their own store), but the *shop attribution* is fully attacker-controlled.

### Recommendation
Include the shop domain (and ideally other trust-relevant headers such as topic/api-version) in the HMAC-signable material, or otherwise independently verify that the `x-shopify-shop-domain` header corresponds to a shop session/registration known to the host application before trusting it for tenant attribution. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification (e.g., cross-checking against an existing installed-shop record).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they own — no special privilege needed).
2. Attacker performs a normal action that triggers a webhook (e.g., creates a product), causing Shopify to POST a legitimately-signed `(raw_body, x-shopify-hmac-sha256)` pair to the app's webhook endpoint.
3. Attacker intercepts/replays that exact `raw_body` and `hmac` value in a forged request to the same webhook endpoint, but sets the header `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body`.
5. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and processes/stores the attacker's event data as if it originated from the victim shop.

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
