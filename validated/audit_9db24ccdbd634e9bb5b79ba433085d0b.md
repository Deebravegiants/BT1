### Title
Webhook `shop-domain` and `topic` Headers Are Trusted But Not Covered by the HMAC Signature, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from HTTP headers, while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body via `to_signable_string`. The identity fields the host application relies on (`shop`, `topic`) are never bound into the signed payload, so any request with a body+HMAC pair that is valid for the app's `client_secret` can be replayed with an attacker-chosen `shop-domain` header and be accepted as authentic.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes an HMAC-SHA256 over `verifiable_query.to_signable_string` and compares it to the received signature using the shared `Context.api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers, which are not part of the signed string at all: [3](#0-2) 

`Registry.process` validates only the HMAC and then dispatches to the handler using the unauthenticated `request.shop` and `request.topic` values: [4](#0-3) 

The binding the app relies on is:
`shop-domain header == tenant that produced the signed body`

but the gem only proves:
`hmac == HMAC(api_secret_key, raw_body)`

Because the same `api_secret_key` is shared across every shop/tenant that has installed the app, and only the body — not the shop identifier — is signed, a genuine webhook delivery captured from one tenant (e.g., an attacker's own store, which they can freely install the app on and receive real, validly-signed webhooks for) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header rewritten to name a different, victim tenant. The `HmacValidator.validate` call still succeeds because it never inspects those headers, and `Registry.process` hands the handler a `WebhookMetadata` object asserting the victim's shop domain and topic while carrying the attacker-controlled body.

### Impact Explanation
Any downstream code that trusts `WebhookMetadata#shop` (or `#topic`) to select the tenant's database record, update inventory, mark an order paid, or otherwise attribute the payload to that shop can be fed attacker-controlled data under another tenant's identity, since the header-derived shop/topic values are unauthenticated relative to this gem's own verification step. This is a cross-tenant identity-binding break: the value used to route/attribute the webhook (`shop`) is disjoint from the value actually authenticated by the HMAC (`raw_body`). It matches the required "cross-tenant access" impact category, since it lets an actor who is a legitimate user of the app on their own shop inject spoofed webhook events attributed to a shop they do not control.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop to receive genuinely-signed webhook deliveries (a standard unprivileged action any Shopify merchant can perform), (2) capturing one such delivery's body+HMAC, and (3) resending it to the app's public webhook endpoint with a modified `shop-domain`/`topic` header naming the victim shop. No secrets, tokens, or privileged access are required beyond what an ordinary app installer already has. The gem performs no additional binding (e.g., signing the shop or topic, or maintaining a per-shop secret) to prevent this replay.

### Recommendation
Bind the shop and topic identifiers into the verified signature material, or otherwise authenticate them independently of attacker-controlled headers, e.g.:
- Extend `to_signable_string` (or a dedicated verification step) to include `shop`, `topic`, and `webhook_id`, not just the raw body, so any mismatch invalidates the signature.
- Alternatively, cross-check the header-derived `shop` against the shop associated with the specific `webhook_id`/subscription server-side (out of scope for this gem, but should be documented as a mandatory host-application check) since the gem itself does not offer this validation.
- At minimum, document prominently that `Request#shop` and `Request#topic` are unauthenticated and must not be trusted for tenant attribution without additional application-level verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the resulting `X-Shopify-Hmac-Sha256: H` header, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (rewritten)
   - Header `X-Shopify-Topic: orders/create` (unchanged or rewritten)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it equal to `H` — validation passes, per [5](#0-4) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: request.parsed_body, ...)`, per [6](#0-5) , causing the host application to process attacker-supplied data as if it originated from `victim.myshopify.com`.

### Citations

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
