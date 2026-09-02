### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the `shop` (and `topic`, `api-version`, `webhook-id`) values are read from HTTP headers that are never included in the signed material. `Registry.process` validates the HMAC and then trusts `request.shop` (taken straight from the unauthenticated header) to construct `WebhookMetadata` that is handed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, outside the signed payload: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` only checks `verifiable_query.to_signable_string` (the body) against the HMAC — it never binds the `shop` header into the signature: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, then passes the header-derived `request.shop` directly into `WebhookMetadata` given to the app's handler, with no cross-check against which tenant actually owns that HMAC-validated body: [4](#0-3) 

The identity binding that should hold is: `shop-domain header == shop that produced this HMAC-signed body`. Because only the body is signed, this equality is never enforced by the library. A user who has a legitimate installation of the app on their own shop receives real webhooks with a valid HMAC (computed with the app's shared `client_secret`, which is the same key for every tenant of the app — not shop-specific). That attacker can replay the exact same raw body (keeping the HMAC valid) to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` still returns `true` because it never looks at the header, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary: the app's webhook handler processes data it will treat as if it originated from the impersonated shop, while it actually validated a payload the attacker fully controls. Depending on how host applications use `WebhookMetadata#shop` (as is standard — e.g., looking up the victim's stored session/access token to act on their store, writing state keyed by shop, or triggering side effects), this enables cross-tenant confusion/injection: an unprivileged internet user who merely has any account with the app installed can inject events attributed to a shop they don't control. This matches the Critical "cross-tenant access" category, since the shop field — the sole tenant identity used to key subsequent operations — is trusted despite not being covered by the cryptographic binding that is supposed to authenticate the request.

### Likelihood Explanation
Likelihood is High for an attacker who can install the app on their own store (the minimal bar for typical public/embedded Shopify apps) — no leaked credentials, secret key, or social engineering is required. They only need to intercept/replay their own genuine webhook delivery with a modified header, which is a normal HTTP capability of anyone who receives webhooks (e.g., via a proxy in their own infrastructure).

### Recommendation
Include the shop-identifying data in the HMAC-signed payload, or otherwise cryptographically bind `shop` to the body before trusting it — e.g., require that `WebhookMetadata#shop` returned to handlers is validated against a shop the app already expects/has a session for, rather than trusting the header outright. At minimum, document (and ideally enforce in code) that consuming apps must cross-check the header-derived `shop` against their own tenant registry before using it, since this gem's `HmacValidator` provides no such guarantee.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook (e.g., `orders/create`) to the app's endpoint; attacker captures the raw request, including the valid `x-shopify-hmac-sha256` header and body.
2. Attacker resends the identical body and HMAC header to the same webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a `Request` object; `HmacValidator.validate` recomputes `HMAC(body, api_secret_key)` and compares — it matches because the body is unchanged. [5](#0-4) 
4. `Registry.process` calls the app-registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, i.e., the host application's handler now believes this attacker-supplied payload originated from the victim shop.

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
