### Title
`ShopifyAPI::Webhooks::Request#shop` returns an unsigned header value while `#to_signable_string` never binds it, allowing forged shop attribution on a genuinely HMAC-valid webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but `#to_signable_string` returns only `@raw_body` and never incorporates that header. `Utils::HmacValidator.validate` therefore only proves the body bytes were signed by *some* valid secret holder — it proves nothing about which shop the request claims to be from — yet `Webhooks::Registry.process` passes `request.shop` straight into `WebhookMetadata` for handler dispatch.

### Finding Description
The claimed binding is: `Request#shop == value covered by to_signable_string`. Tracing the code shows this is false:

- `shop` is derived purely from an attacker-controllable header: `T.cast(shopify_header("shop-domain"), String)` [1](#0-0) 
- `to_signable_string` returns only the raw body, with no shop/header material included: [2](#0-1) 
- `HmacValidator.validate_signature` computes the signature exclusively over `verifiable_query.to_signable_string`, i.e., over `@raw_body` alone: [3](#0-2) 
- `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata` passed to the handler, with no secondary check binding shop to the signed payload: [4](#0-3) 

Because webhook endpoints are public HTTP endpoints (that's the entire reason HMAC verification exists), an attacker who has installed the app on their own shop can obtain a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair by receiving one of their own real webhooks. They can then send a POST directly to the host app's webhook-processing route with that same `raw_body` and `X-Shopify-Hmac-Sha256`, but with `X-Shopify-Shop-Domain` rewritten to `victim-shop.myshopify.com`. `HmacValidator.validate` returns `true` because the signable string (body only) is unchanged, while `request.shop` reports the forged victim domain. No existing guard in this gem's webhook path (`Request#initialize`, `HmacValidator.validate`, `Registry.process`) cross-checks the shop-domain header against the signed content or against a registered-shop allowlist.

### Impact Explanation
Any host application built on this gem that uses `Webhooks::Registry.process` / `request.shop` (as documented) for tenant routing — e.g., looking up the victim's session/access token, writing data keyed by shop, or triggering shop-scoped side effects — will process attacker-controlled webhook payloads under an arbitrary victim shop's identity. This is repeatable against any victim shop domain (real or fabricated) with a single crafted POST per forgery, requiring no interaction with the victim. This matches the Critical "cross-tenant access" category since one tenant's forged request is attributed to and processed against another tenant's identity/data.

### Likelihood Explanation
Preconditions are exactly what the threat model allows: the attacker installs the app on their own shop, registers their own webhook endpoint per the README, and receives a genuinely signed webhook. The only extra step is a direct POST to the host app's webhook endpoint with a rewritten `X-Shopify-Shop-Domain` header — a purely attacker-controlled HTTP request. This requires no secret, no privileged access, and no interaction with the victim, making it low-cost and fully repeatable.

### Recommendation
Do not treat `Request#shop` as trusted/authenticated data derived from an HMAC-covered value. Either (a) require host apps to only accept `request.shop` values that match a shop the app has an active, previously-established session/webhook registration for (defense-in-depth cross-check), or (b) document explicitly that `Request#shop` is unauthenticated header data and must never be used alone for tenant attribution — only `to_signable_string`-covered fields (the body) are integrity-protected by `HmacValidator`. Longer term, `Registry.process` could require callers to supply the expected shop and assert it matches `request.shop` before dispatch, closing the trust gap at the gem level.

### Proof of Concept
Minitest + WebMock/Mocha plan under `test/webhooks/`:
1. Compute `raw_body = '{"id":1}'` and `hmac = OpenSSL::HMAC.hexdigest("sha256", ShopifyAPI::Context.api_secret_key, raw_body)` then Base64-encode it as the `X-Shopify-Hmac-Sha256` header value, simulating the attacker's own genuinely-signed webhook.
2. Build `headers = { "x-shopify-topic" => "orders/create", "x-shopify-hmac-sha256" => Base64.encode64(hmac_bytes), "x-shopify-shop-domain" => "victim-shop.myshopify.com" }` (forged domain, unrelated to the secret owner).
3. `request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)`.
4. Assert `ShopifyAPI::Utils::HmacValidator.validate(request) == true` (HMAC passes because it only covers `raw_body`).
5. Assert `request.shop == "victim-shop.myshopify.com"` (forged, unsigned value accepted as-is), demonstrating the two sides of the claimed binding (`request.shop` vs. content covered by `request.to_signable_string`) diverge while validation still succeeds.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
