This confirms the identity binding break for webhook processing: the OAuth `AuthQuery` correctly includes `shop` in its `to_signable_string` (so `shop` is bound to the HMAC), but the analogous `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `request.shop` is read straight from an attacker-controllable header with no cryptographic binding [2](#0-1) , whereas `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into the signed payload [3](#0-2) .

### Title
Webhook tenant identity (`shop` header) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, never including the `shop-domain` header, yet `ShopifyAPI::Webhooks::Registry.process` dispatches the verified webhook to the app's handler using that same unauthenticated `shop` value as the tenant identity.

### Finding Description
`Utils::HmacValidator.validate` proves only that `verifiable_query.to_signable_string` was signed with `Context.api_secret_key` [4](#0-3) . For webhooks, `to_signable_string` returns solely `@raw_body` [1](#0-0) . The `shop` accessor is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no involvement in the signature computation [2](#0-1) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identifier passed to the app's handler: [5](#0-4) 

The gem's own documentation instructs integrators to route/queue per-tenant work keyed on `data.shop` straight out of `WebhookMetadata`, treating it as trustworthy once `Registry.process` has run: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`. This is the documented, intended API usage, not a host-app misuse.

Because the same `api_secret_key` is used to sign webhooks for every shop that installs the app (it is not per-tenant), the equality this gem is supposed to enforce is:
`shop that generated/owns the HMAC-signed body == shop delivered to the handler as data.shop`.

The gem breaks this equality: the HMAC only proves "a body signed by this app's secret", not "signed for shop X". The `shop` field the handler relies on for tenant scoping is carried in an ordinary, unsigned header.

Contrast with `Auth::Oauth::AuthQuery`, which binds `shop` into the signed payload before computing the HMAC — the correct pattern that `Webhooks::Request` fails to follow [3](#0-2) .

### Impact Explanation
An unprivileged holder of one legitimate webhook delivery for their own shop (any merchant can install the app and receive real, validly-signed webhooks for their own store) can replay that exact `raw_body` + `hmac` pair while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects `shop`. `Registry.process` then invokes the app's handler with `WebhookMetadata#shop` set to the victim's domain while the `body` is actually the attacker's own data. Any host app following the documented pattern (persisting/queuing webhook payloads keyed by `data.shop`) will attribute attacker-controlled data to another tenant — a cross-tenant data-integrity/confusion issue reachable by any merchant who can install the app, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is bounded by the need to obtain at least one genuine signed webhook body/HMAC pair, which any merchant installing the app can trivially obtain by triggering a webhook event on their own store. No access to `api_secret_key`, access tokens, or privileged accounts is required — only a normal webhook subscription on an attacker-owned shop and the ability to POST to the app's public webhook endpoint with modified headers.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the value that is cryptographically bound to the request — e.g., have `Webhooks::Request#to_signable_string` incorporate the shop-domain header alongside the raw body, or require host applications to independently verify that `request.shop` corresponds to a shop with an active installation/session before trusting it for tenant-scoped work, and document this requirement explicitly rather than presenting `data.shop` as already-trustworthy in the webhook handler example.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-topic`.
2. Replay the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because `to_signable_string` only hashes `raw_body`, which is unchanged: [6](#0-5) 
4. `Registry.process` calls the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's data>, ...)` [7](#0-6) , causing the app to process attacker-supplied data under the victim shop's identity.

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
