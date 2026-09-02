## Title
Webhook Cross-Tenant Spoofing via Unauthenticated `shop-domain`/`topic` Headers Not Covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are read directly from unauthenticated HTTP headers. Any request bearer that possesses one valid `(raw_body, hmac)` pair — trivially obtainable by an attacker who owns any shop that installs the app — can replay that pair with an arbitrary `shopify-shop-domain` header and have the library accept it as an authentic webhook for a different, victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` verifies exactly that signable string against the received `hmac`: [3](#0-2) 

None of `shop`, `topic`, `api_version`, or `webhook_id` — all sourced from `shopify_header(...)`, i.e. attacker-controllable HTTP request headers — are part of the signed material: [4](#0-3) [5](#0-4) 

`Registry.process` trusts these unauthenticated fields to route the request to a handler and to build the `WebhookMetadata` that is delivered to the app's business logic, using `request.shop` as the tenant identifier: [6](#0-5) 

The identity binding that should hold is:
`shop_attributed_to_webhook == shop_that_actually_produced_the_HMAC-bound(raw_body)`

Because the HMAC only binds `raw_body`, and `raw_body` (e.g., an `orders/create` payload) does not itself assert which shop it belongs to in a way this library checks, the binding above does not hold. An attacker who is a legitimate merchant with the app installed on their own shop can:
1. Trigger a webhook delivery to their own endpoint (a normal, unprivileged action any merchant can perform, e.g., creating an order).
2. Capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair, both of which are visible to the tenant that receives them.
3. Replay the identical body and HMAC to the app's webhook endpoint while substituting `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `topic`).
4. `HmacValidator.validate` succeeds because the signature only ever covered `raw_body`, which is unchanged.
5. `Registry.process` invokes the registered handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, `WebhookMetadata#topic` and `#api_version`/`#webhook_id` all attacker-chosen.

This lets an unprivileged internet user (any merchant who installs the app) forge webhook events attributed to any other shop of their choosing, breaking the tenant isolation the library is supposed to enforce for webhook processing.

### Impact Explanation
This is a cross-tenant access vulnerability: the library's own webhook-authenticity check (`Utils::HmacValidator.validate`) is the sole gate before dispatching to app handlers, yet it does not bind the `shop` (or `topic`) fields that are handed to the handler as the trusted tenant/topic identity. Any application that persists webhook data keyed by `WebhookMetadata#shop` — the documented and expected usage pattern (see `docs/usage/webhooks.md`) — can be made to write, delete, or act on data under a victim shop's identity using attacker-supplied payload content, without ever needing the victim's or the app's `client_secret`/access token. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
High. Exploitation requires only that the attacker be a normal merchant able to install the target app on their own store (no special privilege) and send a crafted HTTP POST to the app's public webhook endpoint with a modified `shopify-shop-domain` header — something entirely under attacker control since HTTP headers on an inbound request are not authenticated by TLS client certs or any other mechanism in this library.

### Recommendation
Include the tenant-identifying fields (`shop`, and ideally `topic`/`webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., require the app to independently confirm the `shop` against a session/store the app itself created via OAuth before trusting `WebhookMetadata#shop`). At minimum, `Request#to_signable_string` should not omit header-derived identity fields that downstream code (`Registry.process`) treats as authenticated.

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit order from attacker-owned-shop"}'

# Step 1: attacker triggers a real webhook to their own shop and captures (raw_body, hmac)
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
hmac_b64 = Base64.encode64(hmac)

# Step 2: attacker replays the identical body+hmac, but swaps shop-domain header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes because HMAC only ever covered raw_body
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", ...))
```
The handler receives `shop: "victim-shop.myshopify.com"` despite the HMAC never having authenticated that value, demonstrating the cross-tenant identity binding break.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
