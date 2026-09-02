### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `to_signable_string`, defined as the raw request body. The `shop` value (read from the `x-shopify-shop-domain` / `shopify-shop-domain` header) is never part of the signed material, yet `Registry.process` trusts and acts on it directly, passing it into the handler as the tenant identifier.

### Finding Description
`AuthQuery` binds every field it acts on (`code`, `host`, `shop`, `state`, `timestamp`) into `to_signable_string`, so the OAuth callback HMAC covers the `shop` value: [1](#0-0) 

By contrast, `Webhooks::Request` implements the same `VerifiableQuery` interface but signs only the raw body: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` only checks `to_signable_string` against the secret: [4](#0-3) 

`Registry.process` then uses `request.shop` — an unauthenticated header value — as the tenant key handed to the app's handler: [5](#0-4) 

The binding that should hold is: `shop_value_verified_by_hmac == shop_value_acted_on_by_handler`. Before the request: the header `shop-domain` is attacker-controllable and the HMAC only certifies `raw_body`. After `Registry.process`, the handler receives `WebhookMetadata#shop == request.shop`, which was never included in the HMAC computation — so the equality above never actually held; the gem simply assumes it. This mirrors the report's bug class: a field (`shop`) that is acted upon (used to route/attribute the event to a tenant) but not covered by the same authentication check (the HMAC) that gates processing.

Since Shopify signs webhooks using the app's single, app-wide `client_secret` (not a per-shop secret), any webhook the app legitimately receives for any installed shop is a source of a body+HMAC pair that is valid regardless of which shop header accompanies it. An attacker who controls one shop where the app is installed (an unprivileged, non-admin-of-other-tenants actor) can capture one of their own genuine webhook deliveries (body + valid HMAC), then replay that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting a different value in `x-shopify-shop-domain`. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will invoke the handler with the attacker-chosen `shop` value attached to the (attacker's own) body content.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for HTTP webhooks: the `shop` value delivered to app code is unauthenticated even though the overall request "passes" HMAC validation. Depending on how the host app's handler uses `data.shop` (e.g., looking up the shop's session/access token, writing data under that shop's record, or triggering shop-scoped side effects, as shown in the gem's own documented pattern `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), this allows an attacker with only their own shop's app installation to inject or attribute webhook-driven state changes to a different, victim tenant — a cross-tenant access primitive originating from this gem's own webhook-verification code path.

### Likelihood Explanation
Requires only: (1) attacker owns/controls one shop with the app installed (no elevated privileges, no leaked secrets), and (2) attacker can capture one legitimate webhook delivery to their own endpoint and replay it with a modified `shop-domain` header to the same public callback URL. Both are within reach of an ordinary internet-facing merchant/user of the app; no `client_secret` or access token is needed since the HMAC secret is never actually verified against the shop field.

### Recommendation
Bind the shop domain (and ideally topic/webhook id) into the HMAC-covered signable string, or otherwise independently verify that `request.shop` corresponds to a shop the app has an active, legitimate session/installation for before dispatching to handlers. At minimum, document/enforce that consumers must cross-check `data.shop` against their own known-installed-shops list before trusting it, since `Registry.process` currently treats an unauthenticated header as trustworthy tenant identity.

### Proof of Concept
1. App is installed on `shopA.myshopify.com` and `shopB.myshopify.com`.
2. Attacker (merchant/admin of `shopA`) receives a genuine webhook: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`) and `x-shopify-shop-domain: shopA.myshopify.com`.
3. Attacker resends the same `B` and `H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: shopB.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `H` against `HMAC(B, client_secret)` — the shop header is irrelevant: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(shop: "shopB.myshopify.com", body: parsed(B), ...)`, i.e., attacker-supplied data is attributed to `shopB`, a tenant the attacker does not control.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
