### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity used by webhook handlers from the `X-Shopify-Shop-Domain` HTTP header, but this header is never included in the bytes that are HMAC-verified. Only `@raw_body` is signed, so the shop attribution of an otherwise legitimately-signed webhook can be rewritten by anyone who can supply a raw request, breaking the binding between "bytes verified" and "shop acted on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` is read straight from the (attacker-controllable, unsigned) header and is never mixed into the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `to_signable_string`, i.e. the body only: [3](#0-2) 

`Webhooks::Registry.process` trusts `request.shop` unconditionally after this body-only HMAC check passes, and hands it straight to the app's handler as the tenant identity for the event: [4](#0-3) 

Contrast this with `Auth::Oauth::AuthQuery`, which is also a `VerifiableQuery` but explicitly folds `shop` into the signed string, so the shop value *is* bound by the HMAC there: [5](#0-4) 

This is precisely the bug class described in the external report: a check is performed on one input (webhook HMAC over body) while a second field that materially changes behavior (`shop`, the tenant the event is attributed to) is excluded from that check, exactly as `proposedValidators` was excluded from the monopoly check while `activeValidators` was included. Since Shopify apps use a single, shop-independent `client_secret`/`api_secret_key` to sign webhooks for every shop that installs the app, a valid `(body, hmac)` pair obtained for any one shop (including a shop the attacker legitimately controls/installs the app on) remains a valid `(body, hmac)` pair for every other shop, because the shop identifier was never part of the signed content.

**Binding broken (equality that should hold but doesn't):**
`shop_verified_by_hmac == shop_used_by_handler`
Here `shop_verified_by_hmac` is undefined/`∅` (shop is outside the signable string), while `shop_used_by_handler = header("x-shopify-shop-domain")`, an attacker-controlled, unauthenticated value.

### Impact Explanation
Any app that uses `data.shop` from `WebhookMetadata` (the normal, documented pattern per `docs/usage/webhooks.md`) to look up per-tenant session/state, or to authorize a mutating/destructive action (e.g. `app/uninstalled` cleanup, `shop/redact`, `customers/redact`, inventory or order sync) can be tricked into performing that action against a shop the attacker does not control, using a body+HMAC pair obtained from a shop the attacker does control. This is a cross-tenant data/action confusion — the exact "Critical: cross-tenant access" category, achieved without any credential or access-token theft, purely by exploiting the unbound `shop` field.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a shop they control (a normal, unprivileged flow for any Shopify app that supports installation), capture one legitimately-signed webhook delivery from Shopify for that shop, and replay the same body/HMAC to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header swapped to the victim's domain. No secrets, tokens, or privileged access are required — only the gem's own documented webhook-processing entry point (`Webhooks::Registry.process`) is used.

### Recommendation
Include the shop identifier (and ideally the webhook topic/id) as part of the HMAC-signed content check, or otherwise cryptographically bind the `shop` value to the verified body — analogous to how `AuthQuery#to_signable_string` binds `shop` into its signed content. At minimum, `HmacValidator`/`Request` should ensure the `shop` claimed by the header cannot be swapped independently of the verified payload, e.g. by validating that the `shop` header matches shop-scoped signing material, or by requiring the app to separately confirm the shop against its own session store before trusting `data.shop`, and documenting this requirement prominently since the gem does not enforce it.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, receiving legitimate webhook deliveries signed with the app's single `api_secret_key`.
2. Attacker captures one such delivery: `raw_body`, and header `X-Shopify-Hmac-Sha256: <valid_hmac_for_raw_body>`.
3. Attacker POSTs this same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. Server code calls:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(
     ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
   )
   ```
   `Utils::HmacValidator.validate(request)` passes because it only checks `raw_body` against the HMAC — see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim.myshopify.com"` — see `lib/shopify_api/webhooks/registry.rb:198-199` and `lib/shopify_api/webhooks/request.rb:20-23` — even though the payload actually originated from and was signed for `attacker.myshopify.com`.

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
