### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant data attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported bug is a "field used but not the field that was validated" class of error (`convertToShares` used where a direct amount should have been used, decoupling the value acted on from the value actually verified). The equivalent binding break in this gem is in `ShopifyAPI::Webhooks::Request`: the HMAC signature verifies only the raw request body, while the `shop` domain that `ShopifyAPI::Webhooks::Registry.process` uses to attribute the webhook to a tenant is read straight from an HTTP header that is **not** included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over exactly that signable string using the app's single, shop‑agnostic `Context.api_secret_key`: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` — read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never part of the signed payload — to build the tenant-identifying metadata passed to the app's handler: [3](#0-2) [4](#0-3) 

Because `api_secret_key` is the app's single client secret shared across every shop that installs the app (not a per-shop secret), any unprivileged user who controls a shop that has the app installed can produce a genuinely-signed `(raw_body, hmac)` pair from their own store's webhook deliveries, then replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds because the header is outside the signed string, and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim's `shop` with attacker-controlled `body`.

Equality that should hold but doesn't: `shop attributed to the webhook == shop authenticated by the HMAC signature`. Before the request: `signed_bytes = raw_body` only. After: `Registry.process` treats `header.shop` as trustworthy tenant context even though `header.shop ∉ signed_bytes`.

### Impact Explanation
This breaks tenant isolation between shops sharing one app installation: an app built on top of `ShopifyAPI::Webhooks::Registry` receives externally-attacker-forgeable `(shop, body)` pairs where `shop` is unauthenticated. Any handler logic keyed off `data.shop` (e.g., "update this merchant's order/customer record") can be made to write attacker-supplied data into another merchant's tenant context — a cross-tenant access/data-integrity impact.

### Likelihood Explanation
High for any app that (a) has more than one shop install with a shared `api_secret_key` (the standard/expected multi-tenant app model this gem is built for), and (b) trusts `WebhookMetadata#shop` from `Registry.process` as an authenticated tenant identifier — which is exactly the field and call path this gem hands to consuming apps. No credentials, tokens, or privileged access are required beyond having a normal shop installation of the target app to harvest one valid `(body, hmac)` pair.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material, or otherwise cryptographically bind `shop` to the HMAC before exposing it via `WebhookMetadata`. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should not allow `Registry.process` to treat the `shop` header as authenticated when it falls outside `to_signable_string`; document/enforce that consumers must independently verify `shop` against their own installed-shop registry, or extend the signable string to cover the shop domain so the equality `signed_bytes ⊇ {shop, raw_body}` holds.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` (this is a standard, unprivileged install — no special access needed).
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own shop with attacker-chosen body content, and captures the genuine `(raw_body, x-shopify-hmac-sha256)` pair Shopify delivers — this HMAC is valid because it is computed with the app's single `api_secret_key`, per: [5](#0-4) 
3. Attacker POSTs this exact `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` returns `true` (only `raw_body` is checked): [6](#0-5) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`: [7](#0-6) 
6. Any app logic that persists or acts on this data keyed by `data.shop` now applies attacker-controlled content to the victim tenant.

**Uncertainty note:** I could not locate `lib/shopify_api/webhooks/webhook_metadata.rb` in the indexed codebase (only its usage in `registry.rb` was found), so I cannot fully confirm every field it exposes to handler code beyond what is passed at the `WebhookMetadata.new(...)` call site shown above. This does not affect the core finding, which is fully supported by `request.rb`, `hmac_validator.rb`, and `registry.rb`.

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
