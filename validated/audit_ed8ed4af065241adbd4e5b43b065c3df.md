Found a valid analog. The webhook HMAC covers only the raw request body, but the `shop` domain used to route data to a tenant is taken from an unauthenticated header — a direct instance of "a field acted on but not covered by the HMAC."

### Title
Webhook `shop` Domain Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, while the `shop` value that identifies which merchant/tenant a webhook belongs to is read directly from the `x-shopify-shop-domain` HTTP header, which is never included in the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as-is when dispatching to the app's handler, so the `shop` claim used for tenant identification is never actually verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from an unauthenticated header with no binding to the signature: [2](#0-1) 

`HmacValidator.validate` only checks that the computed HMAC of `to_signable_string` (i.e. the raw body) matches the received `hmac` header, using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` relies on this same validation, then immediately forwards the unauthenticated `request.shop` value to the app's handler as the tenant identifier for the webhook payload: [4](#0-3) 

The identity binding that should hold is:
`shop header used for tenant routing == shop the HMAC-signed body actually originated from`

This equality is never checked. The `api_secret_key` used to sign webhooks is the same for every shop that has installed the app — it is not shop-specific. Therefore, any tenant with the app installed on their own shop can obtain a body/HMAC pair that is cryptographically valid (since they legitimately received it from Shopify, or can generate a webhook themselves as an app-owning merchant), then replay that exact `raw_body` + `hmac` header combination to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header pointing at a different (victim) shop that also has the app installed. `Utils::HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: ..., shop: request.shop, ...)` using the attacker-supplied shop value.

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled webhook body (theirs) can be delivered to the app's business logic tagged as belonging to a different merchant's shop. If the host application's webhook handler uses `data.shop` to select which stored session/access token to use for follow-up processing (a common documented pattern in `docs/usage/webhooks.md`), the attacker can inject spoofed webhook payloads under an arbitrary victim shop identifier, corrupting per-tenant state, triggering unwanted actions, or exfiltrating data scoped to that shop — a cross-tenant access impact.

### Likelihood Explanation
This requires only that the attacker themselves have the app installed on their own shop (an unprivileged, ordinary merchant/internet-user position with respect to this app) — no possession of `api_secret_key`, no access token theft, no privileged account is needed. They can capture one legitimate `(raw_body, hmac)` pair from their own webhook deliveries and simply resend it with a forged `shop-domain` header value.

### Recommendation
Bind the `shop` value into the signed payload verification, e.g. include the `shop-domain` header (and `topic`/`webhook-id` if relevant) in the HMAC input, or independently verify that the `shop` header corresponds to a shop with a currently valid, stored session/installation before dispatching to handlers, rather than trusting the raw header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; the app also has a legitimate, unrelated shop `victim-shop.myshopify.com` installed.
2. Attacker triggers (or crafts, since only the body needs to be authentic-looking) a webhook delivery to capture a valid `raw_body` and its corresponding `x-shopify-hmac-sha256` value signed with the shared `api_secret_key`.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because only body is signed (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the payload never originated from that shop.

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
