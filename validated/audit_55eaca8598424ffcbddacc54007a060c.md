### Title
Webhook shop/topic identity spoofing via HMAC that binds only the request body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw HTTP body, then trusts the `shop-domain` and `topic` values taken from unauthenticated HTTP headers to route and tag the event. The binding the gem implicitly claims — "HMAC-valid request" == "request genuinely originated from the shop named in its headers" — does not hold, because the tenant-identifying fields are never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust the header-derived `shop` and `topic` and hands them, unverified, to the app's handler as the tenant/event identity: [4](#0-3) 

Because the `api_secret_key` used to compute the HMAC is shared across every shop that has the app installed (it is the app's own client secret, not a per-shop secret), any merchant who installs the target app on their own store can trigger a legitimate webhook, capture a valid `(raw_body, hmac)` pair, and then replay that exact body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a victim shop's domain or an unrelated topic. `HmacValidator.validate` will report the request as valid — because the body is unchanged — while `Registry.process` dispatches it to the handler labeled with the attacker-chosen `shop`/`topic`.

This is the exact bug class in the report, transposed to this gem's own trust boundary: the equality that should hold is `hmac-verified bytes == bytes that determine tenant identity`, but instead `hmac-verified bytes (body) ⊊ bytes used to bind tenant identity (headers)`.

### Impact Explanation
An app relying on `ShopifyAPI::Webhooks::Registry.process`/`Request#shop` to identify which merchant/tenant a webhook belongs to can be made to process attacker-supplied data (from the attacker's own store, or any store willing to replay a valid signed body) under the identity of a different shop. Depending on what the handler does with `WebhookMetadata#shop` (e.g., looking up that shop's session/access token, updating that tenant's records, billing, or state machines), this can cause cross-tenant data corruption, spoofed cross-tenant events, or a foothold for further tenant confusion — matching the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Any internet user can sign up for a free or trial Shopify store, install a target app that uses this gem's webhook handling, and receive genuinely-signed webhooks for their own shop. Nothing in the gem prevents replaying that valid `(body, hmac)` pair against the same endpoint with a forged `shop-domain`/`topic` header — no additional secret or privileged access is required beyond having the app installed on any single store, which is the normal, expected entry point for an "unprivileged internet user" in a multi-tenant SaaS-style app.

### Recommendation
Bind the tenant-identifying and routing fields into the signed material, or otherwise independently authenticate them:
- Require verification that the `shop` header corresponds to a shop with a currently valid installation/session known to the host app before trusting `WebhookMetadata#shop` for tenant-scoped actions (this needs to be documented/enforced by the gem, since it currently offers no such check).
- Where feasible, prefer webhook delivery/verification mechanisms that cryptographically bind topic/shop to the payload (e.g., verifying against the shop associated with the specific webhook subscription id `x-shopify-webhook-id`, which is unique per subscription per shop, rather than trusting the shop header directly).
- At minimum, document prominently that `Request#shop`/`Request#topic` are unauthenticated header values and must be cross-checked by the host application against known installed shops before being used for tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers any registered webhook topic (e.g., `orders/create`) on their store, capturing the raw POST body `B` and the resulting `X-Shopify-Hmac-Sha256: H` header (computed by Shopify using the app's shared `api_secret_key`).
3. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - `X-Shopify-Topic:` optionally changed to another registered topic
4. `ShopifyAPI::Webhooks::Request.new` parses these headers without validation: [5](#0-4) 
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B`: [6](#0-5) 
6. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, even though nothing from `victim.myshopify.com` produced this request.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
