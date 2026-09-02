### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook payload by computing an HMAC over the raw request body only, but the `shop` (tenant) identity that is later handed to application handlers is read from an unauthenticated header. This breaks the equality that should hold between "the tenant whose signature was verified" and "the tenant the handler acts on," mirroring the root cause pattern in the referenced report (a value used for a security-relevant decision is not the value that was actually verified).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is parsed independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is never included in the signable string: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e. the body — it never considers the shop header: [3](#0-2) 

`Registry#process` trusts this unauthenticated `request.shop` value and forwards it straight into the handler-facing `WebhookMetadata` after only checking the body HMAC: [4](#0-3) 

Contrast this with the OAuth callback path, where `shop` *is* included in the signable string and therefore bound to the HMAC: [5](#0-4) 

So for webhooks the equality that should hold — `shop_verified_by_hmac == shop_used_by_handler` — does not: the gem verifies `hmac == HMAC(body)` but then acts on `shop = header value`, a field never covered by that signature.

### Impact Explanation
Any entity that can install the app on their own shop (an unprivileged action) legitimately receives Shopify-signed webhooks addressed to that shop — a valid `(body, hmac)` pair signed with the app's shared `client_secret`. Because `shop` is not part of the signed content, that same `(body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `Registry.process` will accept it (HMAC still validates) and hand the handler a `WebhookMetadata` claiming to be from the victim shop. Any host logic that keys tenant-scoped behavior off `WebhookMetadata#shop` (e.g. `app/uninstalled` cleanup, GDPR `shop/redact`, `customers/data_request`, order/product sync) can be triggered against a shop the attacker does not own — a cross-tenant identity-binding break, which the rules classify as Critical impact.

### Likelihood Explanation
No secret, access token, or privileged account is required beyond installing the app on the attacker's own store — a standard unprivileged action for any merchant. The attacker only needs to capture a webhook Shopify sends to their own endpoint and resend it with one header changed, which is trivial once the endpoint is internet-reachable (a documented requirement for Shopify webhooks).

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the signed body (e.g., require the host to cross-check `request.shop` against a known, previously-established session/shop record before trusting webhook data), and document this requirement clearly since the current API surface (`WebhookMetadata#shop`) implies the shop value is already trustworthy once `Registry.process` succeeds.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and configures a webhook endpoint they control/observe (e.g. via a proxy) to capture inbound requests.
2. Shopify sends a legitimate webhook to the app for `attacker.myshopify.com`: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the exact same `B` and `X-Shopify-Hmac-Sha256` value to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` — identical to before — and returns `true`, since `shop` is never part of the signed string.
5. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host application to act on behalf of `victim.myshopify.com` using attacker-controlled body content.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
