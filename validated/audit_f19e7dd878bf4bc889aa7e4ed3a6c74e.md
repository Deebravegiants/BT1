### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing a replayed payload to be attributed to a different shop - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the trusted signature only from the raw HTTP body, while the `shop` (tenant) identity is read from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as the authoritative tenant identifier passed to the app's webhook handler, without that value ever being covered by the signature check.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed body and no call into `ShopValidator`: [2](#0-1) [3](#0-2) 

`Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)` and, on success, immediately hands `request.shop` (and the other headers) to the registered handler as trusted tenant metadata: [4](#0-3) 

`HmacValidator.validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string`, i.e. the raw body, and compares it with `OpenSSL.secure_compare`: [5](#0-4) 

The binding that is expected to hold is:

`shop identity trusted by the handler == shop identity bound into the HMAC-verified bytes`

but the actual relationship is:

`HMAC covers only raw_body != shop header value consumed by handler`

Because the `shop-domain` header sits entirely outside the signed material, any party capable of resending or relaying a legitimately-signed webhook payload for shop A (e.g., a previously captured/legit delivery, or any intermediary/log-replay mechanism that can present the same body with a different header set to the app's webhook endpoint) can cause the app to process the webhook while believing it originated from a different shop B, merely by substituting the `shop-domain` header. The HMAC check still passes because it only ever validated the body, not the header claiming which shop it belongs to. Apps built on this gem (per `docs/usage/webhooks.md`) use `WebhookMetadata#shop`/`data.shop` from the handler callback as the trusted tenant key to look up sessions/access tokens and route data — exactly what `Registry.process` passes through unchecked.

This differs from the `Auth::Oauth::AuthQuery`/`JwtPayload` paths in this gem, where the tenant identity (`shop`/`dest`) is embedded inside the signed HMAC query string or JWT payload itself, so it cannot be swapped independently of the signature. The webhook path is the one place where identity and authenticity are split across signed and unsigned channels.

### Impact Explanation
If an attacker obtains any valid (topic, body, hmac) triple — which is not secret and is delivered to every subscribing endpoint including the attacker's own shop's webhooks, or observable via network intermediaries/logs — they can resend it to the app's webhook handler with an arbitrary `shop-domain` header for a victim shop. The HMAC still validates (it only signs the body), so the app's handler will process attacker-supplied data under a shop identity that was never authenticated, i.e. cross-tenant data injection/spoofing into whatever tenant-keyed logic (session lookup, database writes, cache keys, business logic) the host app drives from `data.shop`. This matches the "cross-tenant access" criterion in scope, since the gem's own webhook verification primitive fails to bind the field the host application is documented to trust.

### Likelihood Explanation
Requires only network delivery capability to the app's public webhook endpoint plus knowledge of one valid signed body/HMAC pair for any topic (the attacker's own shop's outgoing webhook, or one captured in transit/logs) — no `api_secret_key`, access token, or privileged account is needed. This is a realistic unprivileged-internet-user replay against the gem's own verification logic, not a host-application misuse issue, since `Registry.process`/`HmacValidator` are the gem's documented verification surface and neither binds the header to the signature.

### Recommendation
Extend `VerifiableQuery#to_signable_string` (or a webhook-specific check) so that the `shop-domain` value is bound into the HMAC computation, or otherwise cryptographically tie the header to the payload (e.g., use the value returned by `HmacValidator` verification to look up the shop from a session store instead of trusting the header directly). At minimum, run `request.shop` through `Utils::ShopValidator.sanitize!` and document/require that host apps not treat `data.shop` from an unauthenticated header as fully trusted without an independent binding to the verified body.

### Proof of Concept
1. Attacker's own shop (or any intercepted delivery) receives a legitimate webhook: body `{"id":123,...}` with header `x-shopify-hmac-sha256: <valid HMAC over body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`, `lib/shopify_api/webhooks/request.rb:20-23`), even though that value was never covered by the signature check — the app now processes attacker data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
