### Title
Webhook HMAC only authenticates the raw body, letting an attacker with any valid webhook replay forge the `shop`/`topic` identity used by the app - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then forwards `request.topic` and `request.shop` to the app's handler as trusted metadata. However, the HMAC signature only covers the raw request body — it never covers the `shop`, `topic`, `webhook-id`, or `api-version` headers that are used to identify the tenant and route the payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` gates entirely on this body-only HMAC check, then immediately trusts the unauthenticated `shop`, `topic`, `webhook_id`, and `api_version` headers to build `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from headers with no cryptographic binding to the HMAC: [4](#0-3) 

This is the "bytes verified versus bytes parsed" identity-binding break: the equality the code implicitly assumes is
`shop_used_for_routing == shop_bound_by_hmac`
but the actual equality enforced is only
`raw_body_bytes == hmac_signed_bytes`,
with `shop` (and `topic`) sitting entirely outside that signed byte range. Anyone who has ever received one genuine webhook for their own shop — i.e., any merchant who has installed the app, a fully unprivileged, unauthenticated-to-other-tenants actor — possesses a `(raw_body, valid hmac)` pair signed with the app's real `api_secret_key`. Because the HMAC only binds to the body, that same `(body, hmac)` pair remains valid no matter what `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` header values are sent alongside it.

### Impact Explanation
An attacker (any merchant who has the app installed, i.e., an unprivileged party relative to *other* tenants) can capture one legitimately-signed webhook body/HMAC pair from their own shop, then replay that exact body to the app's public webhook endpoint while substituting a victim shop's domain in `X-Shopify-Shop-Domain` (and/or a different `X-Shopify-Topic`). `Registry.process` will validate the HMAC successfully (it only checks the body) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop/topic. Any host application that uses `data.shop` to look up the merchant's session/access token or persist data keyed by shop — which is the documented, expected usage pattern of `WebhookMetadata` — will process attacker-controlled data under another tenant's identity, i.e., cross-tenant data injection/spoofing using the app's own trusted webhook channel.

### Likelihood Explanation
High reachability, low attacker cost: no secrets beyond having the app installed on any single shop are required, only the ability to send an HTTP POST to the app's public webhook route with attacker-chosen headers and a previously-observed valid `(body, hmac)` pair. No timing race or privileged access is needed.

### Recommendation
Bind the identity fields into the signed material actually verified, not just the body:
- Cross-check `request.shop` against the shop associated with a known, previously-registered webhook subscription (e.g., look up by `webhook_id` via the Admin API) rather than trusting the header outright, or
- Require host apps to independently verify that the `shop` domain on an inbound webhook matches an existing installed/session shop before acting on the payload, and document this requirement prominently since `Registry.process` currently implies the shop is trustworthy once HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a genuine webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(secret, B)`.
2. Attacker resends an HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only covers `B`)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - `X-Shopify-Topic: orders/create` (unchanged or forged to any registered topic)
3. `ShopifyAPI::Webhooks::Request.new` parses these headers without validation beyond presence: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-derives HMAC over `@raw_body = B`.
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, and any host code that persists or acts on this data keyed by `shop` now processes attacker-supplied content under the victim shop's identity.

### Citations

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
