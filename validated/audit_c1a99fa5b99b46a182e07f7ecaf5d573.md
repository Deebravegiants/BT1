### Title
Webhook HMAC Does Not Cover the `shop-domain` Header, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while the `shop` (tenant identifier) is read from an unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then dispatches the handler using this unverified `shop` value, breaking the binding `shop-that-produced-the-signed-payload == shop-attributed-to-the-processed-event`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only) using the app's shared `api_secret_key`, which is identical for every shop that has the app installed: [3](#0-2) 

`Registry.process` validates only the body's HMAC, then immediately trusts `request.shop` (the unsigned header) to build the `WebhookMetadata` handed to the tenant-specific handler: [4](#0-3) 

Because the app's `api_secret_key` is shared across all shops using the app (it is not shop-specific), any actor who can install the app on a shop they control can legitimately trigger real webhooks with attacker-chosen body content and a validly computed HMAC for that body. Since the `shop-domain` header is excluded from the signed content, that same `(body, hmac)` pair can be replayed to the app's webhook endpoint with the header rewritten to name a different, victim shop. `HmacValidator.validate` still succeeds — it only checks the body against the shared secret — and `Registry.process` dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

This is exactly the "field acted on but not covered by the HMAC" analog called out in the rules: `shop` is acted upon (used as the tenant key for the handler) but is excluded from `to_signable_string`.

### Impact Explanation
An attacker with a self-service install of the app on their own shop can forge webhook events that the host application will process and attribute to any other tenant (e.g., a victim `myshopify.com` domain), since tenant attribution relies solely on the unauthenticated header. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (commonly to look up/update that shop's stored session or data), this enables cross-tenant data injection/corruption or triggering of shop-scoped business logic under a false tenant identity — a cross-tenant access issue.

### Likelihood Explanation
Any application built with this gem that calls `ShopifyAPI::Webhooks::Registry.process` (the gem's documented and only webhook-processing entry point) is exposed, because the gem itself supplies no shop-binding in the signed payload. The attacker only needs the ability to install the app on a shop they control (typical for public apps) to obtain a validly signed body/HMAC pair, then replay it with an altered `shop-domain` header — no access token, `client_secret`, or victim credentials are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value verified against the HMAC (e.g., require re-derivation or independent verification of the shop from a value not solely carried by the mutable HTTP header), or have `Registry.process` cross-check `request.shop` against a shop known to be currently authenticated/associated with the specific webhook subscription before dispatching to handlers.

### Proof of Concept
1. Install the target app (public/self-serve) on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic so Shopify sends a body `B` signed with the app's shared `api_secret_key`, producing header `X-Shopify-Hmac-Sha256: H`.
2. Capture `(B, H)`.
3. Replay a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the headers/body per [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `B` per [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` per [7](#0-6) , causing attacker-controlled data/events to be processed under the victim tenant's identity.

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
