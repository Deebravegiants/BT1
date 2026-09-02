Confirmed: the webhook `shop-domain` header is never part of the HMAC-signed material.

`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `Webhooks::Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is completely outside the signed payload [2](#0-1) [3](#0-2) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (i.e., only `@raw_body`) and `verifiable_query.hmac`, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, with no further binding check between the shop header and the HMAC-covered body [4](#0-3) [5](#0-4) .

### Title
Webhook tenant attribution via unsigned `shop-domain` header bypasses HMAC binding, enabling cross-tenant confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body [6](#0-5) . The tenant identity for the event (`shop`), however, is taken from the `shopify-shop-domain` HTTP header, a value that is never included in the signed material (`to_signable_string` only returns `@raw_body`) [1](#0-0) . The identity binding "shop-domain-header == shop whose secret verified the body" is never enforced.

### Finding Description
`Webhooks::Request` is constructed from `raw_body` and `headers` [3](#0-2) . The class exposes:
- `hmac` — decoded from the `hmac-sha256` header [7](#0-6) 
- `to_signable_string` — returns only `@raw_body` [1](#0-0) 
- `shop` — returns the `shop-domain` header value, unrelated to the signed bytes [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header value using `OpenSSL.secure_compare` [8](#0-7) . This proves only that *the body bytes* were signed by holders of `Context.api_secret_key` (the app's single, shared client secret, used by Shopify for every shop that has installed the app) — it proves nothing about which shop the header claims to be from.

`Registry.process` then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [9](#0-8) 

The binding that should hold is: `shop header value == shop identity cryptographically bound to the signed body`. Because the header is outside `to_signable_string`, this equality is never checked — the gem lets any request with a *validly-signed body* (signed with the app's own single shared secret) carry an **arbitrary, attacker-chosen `shop-domain` header**, and forwards that header value directly to the consuming app's webhook handler as the authoritative tenant identity.

Since Shopify signs webhooks for every shop that installs the app with the *same* `client_secret`, a merchant who has legitimately installed the app (an unprivileged, ordinary "attacker" tenant) receives correctly-HMAC'd webhook deliveries for their own shop. That attacker can replay/craft an HTTP POST to the app's webhook endpoint using a body from their own legitimately-signed webhook (or any body they can get signed, since they control their own shop's events) while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still passes because it never inspected the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce, letting one merchant's traffic be attributed to another merchant inside the host application (e.g. triggering `shop/redact`-style handlers, mutating per-shop billing/subscription state, or otherwise acting on a victim shop's data) purely by controlling the unauthenticated header. This is a cross-tenant access primitive per the specified impact criteria.

### Likelihood Explanation
Likelihood is high for any application that (a) has more than one shop installed with a shared secret, which is the normal Shopify multi-tenant app model, and (b) relies on `request.shop` from `ShopifyAPI::Webhooks::Registry` for tenant attribution as documented/intended by this gem. No credentials beyond a normal, unprivileged app installation are required — exactly the class of "unprivileged internet user" attacker in scope.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header in the HMAC-signable string, or otherwise cryptographically bind the claimed `shop` to the verified body (e.g., verify the header via a per-shop secret, or reject the message unless the previously known access-token/session for that exact shop matches an independent signal). At minimum, `to_signable_string` must not omit fields the application is expected to trust for identity attribution.

### Proof of Concept
1. App has two installed shops: `attacker.myshopify.com` and `victim.myshopify.com`, sharing one `client_secret`.
2. Shopify sends a legitimate webhook to the app for `attacker.myshopify.com` with body `B` and header `X-Shopify-Shop-Domain: attacker.myshopify.com`, HMAC = `HMAC(secret, B)`.
3. Attacker captures this request (they own that shop, so this is trivial — e.g. via a local proxy on their own store activity) and resends it to the app's webhook endpoint, keeping body `B` and HMAC unchanged, but replacing the header with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers).shop` returns `"victim.myshopify.com"` [2](#0-1) .
5. `HmacValidator.validate` still succeeds because it only checks `B` against the HMAC [5](#0-4) .
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [10](#0-9) , causing the host app to act as though the event came from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
