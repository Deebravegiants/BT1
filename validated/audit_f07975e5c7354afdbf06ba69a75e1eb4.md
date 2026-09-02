### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and is verified via `Utils::HmacValidator.validate` in `ShopifyAPI::Webhooks::Registry.process`. The HMAC check only covers the raw request body: `to_signable_string` returns `@raw_body` alone [1](#0-0) , and `HmacValidator.validate_signature` computes the HMAC over that signable string using the shared app secret [2](#0-1) . The `shop` value, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, completely outside of the signed payload [3](#0-2) .

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . Because the same `api_secret_key` is shared across every shop/tenant that has the app installed, the HMAC computed over the body is valid for **any** shop that produces that exact body — the signature carries no binding to the `shop` header at all. The identity binding that should hold is:

`shop asserted in webhook == shop cryptographically bound to the signed bytes`

but the implementation only checks `hmac(body) == valid`, never `shop ∈ signable_string`. This is exactly the reachable analog of the reported bug class: a field ("shop") is acted upon (used to route/tag the event to a tenant) but is not covered by the verification (HMAC).

### Impact Explanation
A malicious but otherwise unprivileged actor who has installed the app on their own shop (any attacker can do this for free on Shopify) receives legitimate webhooks for their own store, each with a valid HMAC over the body computed with the app's shared secret. Because the shop header is unauthenticated, that same `(raw_body, hmac)` pair remains valid when replayed with a different `shopify-shop-domain` header value naming a victim shop that also uses the same app. `Registry.process` will accept the forged request (HMAC passes) and dispatch it to the app's webhook handler tagged as belonging to the victim shop [4](#0-3) . Any host application that trusts `WebhookMetadata#shop` to select which tenant's data to update (a very common pattern) can be tricked into writing attacker-controlled data into a different tenant's records, or into believing that state changes (e.g. `orders/updated`, `app/uninstalled`) occurred for a shop they don't own. This is a cross-tenant integrity/isolation break driven directly by this gem's verification logic, which meets the Critical bar (cross-tenant access).

### Likelihood Explanation
Exploitation only requires installing the app once (no privileged access, no leaked secret, no social engineering) and capturing one's own valid webhook body/HMAC pair, then replaying it with a modified header value against the app's public webhook endpoint. The `Request` header-parsing code makes no attempt to bind `shop` to the signed bytes [5](#0-4) , so this is trivially reproducible by anyone with a store and app install.

### Recommendation
Include `shop` (and ideally `topic`) in the signable string used for HMAC verification, or otherwise cryptographically bind the asserted shop to the verified bytes before constructing `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host application against its own known/installed-shop list before being trusted for tenant routing.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any webhook event, capturing the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify — this HMAC is valid because `HmacValidator.validate_signature` only signs `@raw_body` [1](#0-0) .
2. Attacker resends the identical body and HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers without error (all required headers present) [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is unchanged [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop [7](#0-6) , demonstrating the cross-tenant identity-binding break.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
