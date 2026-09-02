### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` identity used to route and attribute the webhook payload comes from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts this unauthenticated `shop` value to build the `WebhookMetadata` that is handed to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately forwards `request.shop` (the unverified header) into `WebhookMetadata`, which is the sole shop-identity signal the host application receives to attribute the payload to a tenant: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, which for webhook requests is the body only — the `shop` field is never part of what is verified: [4](#0-3) 

This is the same class of bug flagged in the referenced report: a field that is acted upon (`shop`, used to determine which tenant's data the webhook body belongs to) is not covered by the integrity check (the HMAC binds only the raw body). The binding that should hold — `shop_header == shop_that_produced(hmac, body)` — does not, because the HMAC never incorporates `shop` at all. Any attacker who can obtain one legitimately-signed webhook body/HMAC pair (e.g., by installing the app on their own shop and receiving a real webhook) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. The signature still validates because the header isn't part of the signed content, yet the host application will process/store the payload as if it belongs to the spoofed shop.

### Impact Explanation
This crosses a tenant boundary using unprivileged means: an attacker who legitimately controls their own shop (and thus receives real, validly-signed webhooks for it) can cause the app to associate that webhook's data with a victim shop of the attacker's choosing, since `WebhookMetadata#shop` — the only tenant identifier the gem exposes to the handler — is taken from an unauthenticated header. Depending on what the host handler does with `data.shop` (e.g., look up/update records keyed by shop domain), this enables cross-tenant data injection/corruption without needing the victim's credentials, access token, or `client_secret`.

### Likelihood Explanation
Requires only: (1) the attacker to be a valid, registered shop for the target app (a normal, unprivileged merchant/install, not a privileged account), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a captured body/HMAC pair and a forged `shop-domain` header. No secrets, TLS interception, or social engineering are needed — this is reachable purely through the gem's own webhook verification logic, which is documented as validating "the webhook" but in fact only authenticates the body, not the shop attribution.

### Recommendation
Do not treat `request.shop` as authenticated. At minimum:
- Document prominently that `WebhookMetadata#shop` is derived from an unauthenticated header and must be cross-checked by the host app against a shop it already has a session/webhook registration for (defense already possible, but not enforced by the gem).
- Where feasible, have `Registry.process` (or an opt-in strict mode) reject requests whose `shop` header does not correspond to a shop with an active session/registration known to the caller, or bind `shop` into the signable string comparison used for validation when the topic/registration data is available.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a real webhook, e.g. `orders/create`, with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC over raw body B>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - raw body `B`
2. Attacker replays the exact same raw body `B` and the exact same `x-shopify-hmac-sha256` value to the same app endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the HMAC against the raw body (`to_signable_string` returns `@raw_body`), never checking the `shop` header: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host app to process the attacker's crafted order payload as though it belongs to the victim shop. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
