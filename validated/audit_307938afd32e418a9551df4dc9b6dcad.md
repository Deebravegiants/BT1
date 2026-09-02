This confirms the asymmetry: for OAuth callbacks, `AuthQuery#to_signable_string` in `lib/shopify_api/auth/oauth/auth_query.rb:34-43` explicitly includes `shop` in the signed string, so the shop identity is cryptographically bound to the HMAC. But for webhooks, `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb:36-38` returns only `@raw_body` — the `shop` value (read from the `x-shopify-shop-domain`/`shopify-shop-domain` header via `Request#shop`, `lib/shopify_api/webhooks/request.rb:20-23`) is never part of the signed bytes, yet `Registry.process` in `lib/shopify_api/webhooks/registry.rb:189-199` trusts `request.shop` to construct `WebhookMetadata` dispatched to the app's handler.

### Title
Webhook Shop-Domain Header Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `Registry.process` trusts the unauthenticated `x-shopify-shop-domain` header as the tenant identity passed to the app's webhook handler. Anyone who possesses one valid `(raw_body, hmac)` pair for a topic (trivially obtainable by installing the app on a shop they control and receiving a real webhook) can replay it against the app's webhook endpoint with an arbitrary `shop` header, and `HmacValidator.validate` will still report success because the shop value is not part of the signed content.

### Finding Description
`HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) verifies `verifiable_query.hmac` against `HMAC(secret, verifiable_query.to_signable_string)`. For webhooks, `to_signable_string` returns `@raw_body` only (`lib/shopify_api/webhooks/request.rb:36-38`), and `Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`) is read straight from an HTTP header that is not part of that signed string. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) then builds `WebhookMetadata` using `request.shop` after only checking `Utils::HmacValidator.validate(request)`, and passes it to the app-registered handler as the shop the webhook is "from."

Equality that should hold but doesn't: `bytes_verified_by_hmac == bytes_used_to_determine_tenant`. Before the attack: a legitimate webhook for shop A has `hmac == HMAC(secret, body_A)` and `shop == "A"`. After the attack: the attacker resends `body_A`/`hmac` unchanged but sets the `shop-domain` header to `"B"`. `HmacValidator.validate` still returns `true` (it only checks `body_A` against `hmac`), but `Registry.process` now dispatches `WebhookMetadata.new(shop: "B", body: body_A, ...)` to the handler — the app believes body content genuinely produced for shop A actually belongs to shop B.

This directly mirrors the report's root cause pattern: a value used for identity/ownership resolution (`dao`/`token`/`lpTokenId` in the Solidity report; `shop` here) is taken from attacker-controlled input instead of being bound to the verified data, in contrast to the correctly-bound `AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`) which does include `shop` in the signed string for the OAuth callback path.

### Impact Explanation
Any app built on this gem that keys business logic off `WebhookMetadata#shop` (e.g., updating per-shop state, revoking or rotating stored access tokens on `app/uninstalled`, processing GDPR `customers/redact` or `shop/redact` payloads, or writing merchant data) can be made to apply attacker-controlled but validly-signed body content to an arbitrary victim shop's tenant context, without ever needing that victim's credentials. This is a cross-tenant integrity/isolation break: data or state changes intended for shop A get attributed to and applied against shop B purely by header manipulation, satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
Exploitation only requires the attacker to install the app on any shop they control (or observe a webhook via any other means) to obtain one valid `(raw_body, hmac)` pair for a topic of interest, then POST that identical body/hmac to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header naming the victim shop. No secret, token, or privileged access is required — only network access to the app's webhook endpoint, which is unprivileged-internet-reachable by design.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed content, or otherwise cryptographically/contractually bind the `shop` value used for dispatch to the verified payload — analogous to how `AuthQuery#to_signable_string` binds `shop` for OAuth callbacks. At minimum, `Registry.process` should not trust `request.shop` for tenant-sensitive handling unless it is bound to the HMAC-verified bytes; alternatively, require callers to independently correlate `request.shop` against the shop associated with the offline/online session used to register that webhook subscription before acting on the payload.

### Proof of Concept
```ruby
# 1. Attacker installs the app on shop-attacker.myshopify.com and receives a genuine
#    webhook (e.g. products/update) with body B and header:
#      x-shopify-hmac-sha256: H = HMAC(secret, B)
#      x-shopify-shop-domain: shop-attacker.myshopify.com

# 2. Attacker replays the exact same body B and hmac H to the app's webhook endpoint,
#    but with the header changed:
headers = {
  "x-shopify-topic"        => "products/update",
  "x-shopify-hmac-sha256"  => H,                     # unchanged, still valid for B
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)

# 3. HmacValidator.validate only checks B against H -- it never looks at the shop header,
#    so validation succeeds:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the app's handler with shop: "victim-shop.myshopify.com"
#    even though body B was never produced for that shop:
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(topic: "products/update",
#                                           shop: "victim-shop.myshopify.com",
#                                           body: parsed(B), ...))
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
