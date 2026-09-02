### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook processing pipeline authenticates only the *body* of an inbound webhook via HMAC, while the `shop` identity used to route and label the payload for the host application's handler is taken from an unauthenticated header. This breaks the equality: `bytes covered by HMAC (raw_body)` != `bytes used to identify the tenant (X-Shopify-Shop-Domain header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the signed content: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` (the body) against `verifiable_query.hmac`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` performs this HMAC check and then, without any additional binding, forwards the unauthenticated `request.shop` into the `WebhookMetadata` struct that is handed to the host application's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

By contrast, the OAuth `AuthQuery#to_signable_string` explicitly *includes* `shop` in the signed content, demonstrating that this gem's own design intent is for `shop` to be part of the HMAC-verified data when it is used as an identity field: [6](#0-5) 

Shopify signs webhooks for an app using a single per-app `client_secret` shared across every shop that has installed the app — it is not a per-shop secret. This means any unprivileged internet user who installs the app on their own store (a completely legitimate, unprivileged action) can obtain a genuine, HMAC-valid `(raw_body, hmac)` pair for their own webhook events. Because `to_signable_string` for webhooks never includes `shop`, that same valid `(raw_body, hmac)` pair remains valid under `HmacValidator.validate` regardless of what `X-Shopify-Shop-Domain` header value accompanies it. An attacker can therefore replay a legitimately-signed webhook body while substituting an arbitrary victim shop domain in the header, and `Registry.process` will pass HMAC validation and hand the host application a `WebhookMetadata` object whose `shop` field falsely claims to be the victim's store.

### Impact Explanation
This is a cross-tenant identity confusion vulnerability at the gem level: the gem authenticates the payload bytes but not the tenant-identifying field it exposes as authoritative in `WebhookMetadata#shop`. Any host application that follows the gem's documented/intended usage — i.e., trusts `data.shop` from a successfully-`process`-ed webhook as the shop the event pertains to (exactly as the struct and API imply) — will process attacker-controlled data under a victim shop's identity. Depending on the handler's logic (e.g., updating shop-scoped records, disabling features, writing audit logs, revoking access, syncing inventory) this can result in cross-tenant data corruption or state changes attributed to a shop that never sent the event, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Requires only: (1) attacker installs the app on any shop they control (a normal, unprivileged, unauthenticated-from-Shopify's-perspective action available to any merchant), (2) attacker triggers or waits for a real webhook event from their own store to capture a valid `(body, hmac)` pair, (3) attacker replays that body/hmac to the app's public webhook endpoint with a forged shop-domain header. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Bind `shop` into the HMAC-verified surface for webhooks, mirroring the OAuth `AuthQuery` pattern — e.g., have `Webhooks::Request#to_signable_string` incorporate the shop-domain header (and/or have `HmacValidator`/`Registry.process` independently confirm that the shop asserted in the header matches an already-established, verified relationship for that specific webhook subscription) before exposing it as the trusted `WebhookMetadata#shop`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-scoped authorization without additional verification against Shopify.

### Proof of Concept
1. Register the app on attacker-controlled shop `attacker-shop.myshopify.com` and capture a real webhook delivery, e.g. `orders/create`, noting the raw request body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid because it's HMAC-SHA256(`B`, app's `client_secret`)).
2. Replay to the app's webhook endpoint:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>
X-Shopify-Api-Version: 2024-01

B
```
3. `ShopifyAPI::Webhooks::Registry.process` computes HMAC over `B` only (`Request#to_signable_string`), which matches `H`, so `HmacValidator.validate` returns `true`.
4. The handler registered for `orders/create` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` — the gem hands the host application attacker-controlled data falsely labeled as belonging to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
