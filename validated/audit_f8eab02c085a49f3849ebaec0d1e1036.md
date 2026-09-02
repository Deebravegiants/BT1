### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, while the HMAC signature verified by `Utils::HmacValidator` only covers the raw request body. `Registry.process` accepts any request whose body HMAC validates and then hands the handler a `shop` value that was never part of what was signed, breaking the invariant "shop claimed == shop authenticated."

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`shop` is read straight from an HTTP header that plays no part in that signable string: [2](#0-1) 

`Registry.process` validates the HMAC of the body/secret pair, then immediately trusts `request.shop` (the header) to build the `WebhookMetadata` passed to the app's handler, without any check that the shop matches what was actually signed: [3](#0-2) 

`Utils::HmacValidator.validate` only proves the *body* was produced with the app's `client_secret` — it says nothing about which shop it belongs to, since the same `client_secret` is shared across every shop that has the app installed: [4](#0-3) 

This is the exact bug class described in the reference report, generalized from "accounting values not covered by validation" to "identity fields not covered by validation": the equality that should hold is `shop_header == shop_bound_by_HMAC(body)`, but the code only checks `HMAC(body) == received_signature`, never binding `shop_header` into that signature. Compare this to `Auth::Oauth::AuthQuery`, which correctly includes `shop` in its `to_signable_string` and is thus properly bound to the HMAC: [5](#0-4) 

The webhook path has no equivalent binding for `shop`.

### Impact Explanation
Because the `client_secret` (and therefore the HMAC key) is identical for every shop that has the app installed, any validly-signed webhook body/HMAC pair legitimately obtained for shop A can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to shop B. `Registry.process` will pass the HMAC check (it only checks the body) and will invoke the handler with `WebhookMetadata#shop == "shop-b.myshopify.com"` even though the payload was never generated for shop B. Any host application that uses `data.shop` from `WebhookMetadata` to resolve which tenant's session/data to act on (a documented, expected usage pattern of this gem) will act on shop B's identity using attacker-supplied/foreign data — this is cross-tenant confusion/access, which the rubric classifies as Critical impact.

### Likelihood Explanation
The attacker only needs to be a legitimate merchant/developer that has the app installed on their own store (an unprivileged internet user with respect to *other* tenants) and needs to be able to capture one valid webhook delivery for their own shop (e.g., via their own reverse proxy/logging in front of their own receiving endpoint during development, or any setup where they can observe the raw bytes Shopify sends them). No access to `api_secret_key` or to any other merchant's credentials is required — only reuse of a validly-signed payload they legitimately received for their own tenant, replayed with a forged header value. This matches the "unprivileged internet user" threat model in scope.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable string, or otherwise cryptographically tie the shop domain to the signed body — e.g., include it as part of the canonical string validated by `Utils::HmacValidator`, matching the pattern already used in `Auth::Oauth::AuthQuery#to_signable_string`. At minimum, `Registry.process` should cross-check `request.shop` against an independently-verified value (such as a per-shop webhook signing secret, or a shop value embedded in and covered by the signed payload) before constructing `WebhookMetadata` and invoking the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they legitimately control) and triggers a webhook event (e.g., `orders/create`).
2. Attacker captures the raw request Shopify sends to the app's webhook endpoint for `attacker-shop.myshopify.com`, including the `x-shopify-hmac-sha256` header and raw body — both valid because they were produced with the app's shared `client_secret`.
3. Attacker replays the exact same body + HMAC header to the app's webhook endpoint again, but rewrites `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks `body` against `Context.api_secret_key`), per [6](#0-5) .
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` per [7](#0-6)  and invokes the app's handler, which now processes attacker-controlled webhook content under the victim shop's identity.

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
