### Title
Webhook Shop Domain Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop as soon as `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only covers the raw request body — never the `shop-domain` header that the registry uses to attribute the event to a tenant. An attacker who owns/controls a shop that has installed the app can capture one of their own legitimately-signed webhook deliveries and replay the identical body+signature to the app's webhook endpoint while substituting a victim shop's domain in the `X-Shopify-Shop-Domain` header, causing the handler to process attacker-controlled data as if it came from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the unauthenticated header, entirely outside the HMAC-signed data: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the body) and compares it against the received signature: [3](#0-2) 

`Registry.process` only gates on this HMAC check, then forwards the header-derived `request.shop` straight to the handler as the tenant identity for the event: [4](#0-3) 

Because the app's `client_secret` (used as the HMAC key) is shared across every shop that installs the app, any merchant who installs the app receives legitimately-signed webhooks for their own shop. Since `shop-domain` is not part of the signed payload, that same (body, hmac) pair remains valid when replayed with a different `shop-domain` header — the gem has no way to detect the substitution. This breaks the intended binding: `hmac-verified-body == verified-identity`, when in fact identity (`shop`) is asserted, not verified.

### Impact Explanation
This allows cross-tenant data confusion: an attacker-controlled shop can force the host application to process arbitrary (but validly-signed) webhook payloads under a victim shop's identity. Any downstream logic in the host app keyed off `WebhookMetadata#shop` (e.g., updating that shop's stored data, triggering emails, billing changes, or session/data lookups scoped by shop) can be manipulated to act on the wrong tenant, which falls under cross-tenant access — a Critical-tier impact per the given scope.

### Likelihood Explanation
The prerequisite is only that the attacker controls one shop that has installed the app (any unprivileged merchant/dev store can do this) and can reach the app's public webhook endpoint. No secrets, tokens, or privileged access are required — only capturing one delivered webhook (body + `X-Shopify-Hmac-Sha256` header) from their own install and replaying it with a different `shop-domain` header, which is straightforward with basic HTTP tooling.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-covered signable content, or otherwise independently bind/verify the `shop-domain` header (e.g., against a value cryptographically tied to the signed payload) before it is trusted as the tenant identifier passed to `WebhookMetadata`. At minimum, document/require host apps to cross-check `request.shop` against the merchant that has an active webhook subscription/session, but the gem itself should not present `HmacValidator.validate` as validating the whole `Request` object when it omits fields host apps rely on for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggers an event (e.g., `orders/create`), and captures the resulting webhook POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(client_secret, B)`).
2. Attacker resends the same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and `X-Shopify-Topic` as desired).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation succeeds since `shop-domain` is not part of the signed string: [5](#0-4) 
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's data>, ...)`, and the host app processes attacker-supplied data under the victim's tenant identity.

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
