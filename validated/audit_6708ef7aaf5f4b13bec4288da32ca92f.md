### Title
Webhook `shop-domain` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` value used downstream by webhook handlers is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header. Because the app's webhook secret (`Context.api_secret_key`) is shared across every shop that installs the app, any merchant who can trigger one legitimate webhook delivery for their own store can capture a valid `(body, hmac)` pair and replay it against the same public webhook endpoint with a different `shop-domain` header, causing `ShopifyAPI::Webhooks::Registry.process` to accept the forged request and hand the handler a spoofed shop identity.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the supplied `hmac`: [1](#0-0) 

For webhooks, `Webhooks::Request` implements this contract as: [2](#0-1) 

`to_signable_string` returns only `@raw_body` — the `shop` attribute (sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is never included in the signed bytes: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identity handed to the app's handler: [4](#0-3) 

Because `Context.api_secret_key` is a single, app-wide secret (not per-shop), the same valid `(raw_body, hmac)` pair is valid regardless of which shop it is claimed to originate from. This breaks the intended identity binding: `authenticated_bytes (raw_body) != shop_identity_used_by_handler (header)`. This is the same class of bug as the analog report — a value that is *acted upon* (here, `shop`, used to attribute the event to a tenant) is not the value that is *covered by the HMAC* (here, only the raw body).

### Impact Explanation
Any unprivileged internet user who can get the target app to deliver one webhook to them (e.g., by installing the app on their own free/test store and triggering `orders/create`, `app/uninstalled`, etc.) obtains a `(raw_body, hmac)` pair that is valid for *every* shop that has installed the app, because the signature never binds to `shop-domain`. They can then POST that exact body and HMAC to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header value (e.g., a victim shop's domain). `Registry.process` will pass HMAC validation and invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen value. Any host application that uses `data.shop` to look up per-tenant records, sessions, or to gate/attribute mutating actions (which is exactly the intended and documented usage pattern) will process attacker-controlled data as belonging to a shop it does not control — a cross-tenant data/identity injection.

### Likelihood Explanation
The webhook endpoint is intentionally public/unauthenticated (that's the point of HMAC-based verification instead of a session). Obtaining a valid signed payload only requires being a legitimate — even trial/free — merchant who installs the app once, which is achievable by any internet user without any leaked credentials, TLS interception, or privileged access. Forging the header on replay requires no cryptographic secret at all.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable material, or otherwise cryptographically bind `request.shop` to the verified payload before it is handed to the handler, e.g.:
```ruby
sig { override.returns(String) }
def to_signable_string
  "#{shop}\n#{@raw_body}"
end
```
so that a valid signature for one shop cannot be replayed for another. At minimum, document and enforce that `WebhookMetadata#shop` must never be trusted as an authenticated tenant identifier by consuming applications unless additionally cross-checked against an independently verified session/shop record.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and lets it deliver a normal webhook (e.g., `orders/create`) to the app's public webhook endpoint, capturing the exact `raw_body` and `x-shopify-hmac-sha256` value from that request.
2. Attacker replays the identical `raw_body` and `hmac` header to the same endpoint, but swaps `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks `raw_body`, which is unchanged: [5](#0-4) .
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host application to attribute the attacker's payload to the victim tenant: [6](#0-5) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
