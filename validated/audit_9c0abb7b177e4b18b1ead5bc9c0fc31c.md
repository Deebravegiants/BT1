### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)`, which HMACs that signable string with the app's `client_secret` [2](#0-1) [3](#0-2) . The `shop` value handed to the application's webhook handler, however, is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [4](#0-3) . Because the shop identity is never part of the signed bytes, the binding "HMAC-authenticated bytes == the tenant the handler acts on" does not hold.

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the request [5](#0-4) . For `Webhooks::Request`, `to_signable_string` is defined as `@raw_body` only [1](#0-0)  — none of the HTTP headers, including `shop-domain`, are part of the signed payload.

`Registry.process` performs exactly one authentication check — the HMAC — and then immediately trusts `request.shop` to build `WebhookMetadata`, which is passed to the app's handler as the tenant identifier: [2](#0-1) 

Because the same app-wide `client_secret` is used to sign webhooks for every merchant using the app, any shop that has this app installed can receive a legitimately-signed webhook (valid `hmac` for some `raw_body`), and then replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still pass (the body/HMAC pair is genuinely valid), but `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` field is attacker-controlled and unrelated to the actually-signed body.

This is the same class of bug identified in the source report: a value used to determine "which tenant/channel this data belongs to" is not covered by the cryptographic authentication that gates processing (there, channel-id vs. packet HMAC/ack; here, `shop` header vs. webhook-body HMAC). The equality that should hold — `shop asserted in the authenticated envelope == shop the handler acts on` — is broken because `shop` is sourced from `shopify_header("shop-domain")` [6](#0-5) , a value outside the HMAC boundary.

### Impact Explanation
Applications built on this gem typically use the `shop` field from `WebhookMetadata` to look up per-tenant sessions/access tokens or to attribute incoming webhook data (orders, customer data, redact requests, etc.) to a specific merchant. An attacker who legitimately installs the app on their own store can obtain a genuinely-signed webhook body/HMAC pair, then replay it with a forged `shop-domain` header pointing at a victim merchant. Any host application that trusts `WebhookMetadata#shop` for tenant-scoped effects (writing data under the victim's tenant, triggering victim-scoped side effects, or fetching/attaching the victim's access token via that shop) is exposed to cross-tenant data injection/confusion — this matches the Critical "cross-tenant access" impact category, since the boundary crossed is between one merchant's authenticated payload and another merchant's tenant identity.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the app on an attacker-controlled shop to legitimately receive at least one signed webhook, and (2) direct HTTP access to the app's public webhook endpoint (which by design accepts unauthenticated internet traffic, gated only by this HMAC check). No access token, `client_secret`, or privileged account is required — both are properties of an ordinary, unprivileged merchant/internet user, keeping this within the stated threat model.

### Recommendation
Bind the shop identity into the authenticated data before trusting it: either include the `shop-domain` header in the HMAC-signed payload (not possible without a Shopify-side change), or — within this gem — have `Registry.process` cross-check `request.shop` against context the host app independently trusts (e.g., require the caller to supply the expected shop and compare, rather than exposing an unauthenticated `shop` field as if it were verified). At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must not be used as a sole tenant-selection key without additional verification (e.g., matching against a shop that already has a known, previously-established session).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with body `B`, receiving a genuinely Shopify-signed request with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker sends a forged HTTP POST directly to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid for `B`), but `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) , which recomputes HMAC over `@raw_body` (`B`) only [1](#0-0)  — validation succeeds.
4. `Registry.process` builds `WebhookMetadata.new(topic:, shop: request.shop, ...)` using the forged `shop` value `victim.myshopify.com` [8](#0-7)  and invokes the app's handler, which now processes attacker-supplied data attributed to the victim's tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
