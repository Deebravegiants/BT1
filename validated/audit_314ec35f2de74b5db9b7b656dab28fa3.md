### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`, `webhook_id`, `api_version`) from unauthenticated HTTP headers, while `to_signable_string` — the value verified by `Utils::HmacValidator` — is computed from the raw body alone. Because the shop identity is acted upon (passed to the app's webhook handler) without being covered by the HMAC, any party who can obtain one genuine, validly-signed webhook (e.g. by installing the app on their own store) can replay that exact body+HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header, and `Registry.process` will accept it as authentic for the spoofed shop.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates only the body HMAC and then dispatches the handler using `request.shop` as the tenant identity, with no check that the header is consistent with anything cryptographically bound to the body: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the body) and the app's shared `client_secret`: [4](#0-3) 

The binding that should hold is: `hmac == HMAC(shop ∥ topic ∥ body, client_secret)` so that the shop attribution is cryptographically tied to the signature. Instead the actual binding is `hmac == HMAC(body, client_secret)`, independent of `shop`. Any user who can obtain a single genuine webhook delivery for the app (trivial: install the app on their own development store, which any unprivileged internet user can do) possesses a `(raw_body, hmac)` pair that remains valid under `HmacValidator.validate` for *any* shop-domain header value, because the app's `client_secret` is shared across all installations of the app, not shop-specific.

### Impact Explanation
This breaks the tenant-identity binding relied upon by the host application: `WebhookMetadata#shop`, sourced from `request.shop`, is the field apps use to know which merchant record a webhook belongs to. An attacker can therefore submit an HMAC-valid request (using a webhook they legitimately received for their own shop) to the app's registered webhook endpoint while spoofing the `shop-domain` header to a victim's `myshopify.com` domain. The library will treat it as an authentic message from the victim shop and hand attacker-controlled body content to the app's handler under the victim's tenant identity — a cross-tenant data/action injection, which is the analog of the reported bug class (a value that drives a security-relevant decision but is excluded from the verified/HMAC-covered data).

### Likelihood Explanation
Likelihood is moderate-to-high in any app that is publicly installable (the normal Shopify app distribution model): obtaining one genuine signed webhook only requires installing the app once on an attacker-controlled store, which needs no privileged credentials, tokens, or secrets — only interaction the gem is designed to support for arbitrary merchants.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable content, or otherwise cryptographically bind the `shop-domain` header to the signed payload before trusting it for tenant attribution. At minimum, document and enforce that `request.shop` must not be treated as authenticated by `HmacValidator.validate`, and provide a per-shop verification mechanism (e.g., cross-check against a known/expected shop for the delivery, or require Shopify's webhook signing keys that bind headers) so a valid HMAC for one shop cannot be replayed as if it belonged to another shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid because `H == HMAC(B, client_secret)`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the request to the app's webhook endpoint, keeping `body=B` and `hmac=H` unchanged, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the spoofed headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, client_secret)` — still equal to `H` — so validation passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it originated from `victim.myshopify.com`.

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
