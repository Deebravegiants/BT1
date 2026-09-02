## Analysis

I mapped the FLUX-token bug class (a value is trusted/acted upon without being covered by the binding that's supposed to authenticate it) to this gem's webhook verification path.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers, with no involvement in the signable string: [2](#0-1) 

`Webhooks::Registry.process` verifies only the body/HMAC pair, then dispatches to the handler and builds `WebhookMetadata` directly from the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it to the `hmac` header — again, only over the body: [4](#0-3) 

### The broken binding

The equality the gem needs to guarantee is:
`shop asserted in x-shopify-shop-domain header == shop that Shopify actually generated this HMAC-signed body for`

But since `api_secret_key` is a single **app-wide** secret shared across every shop that installs the app (not a per-shop secret), and `shop`/`topic` are excluded from the signed string, that equality is never checked. Any `(body, hmac)` pair that is valid for *any* shop using the app (e.g. one the attacker legitimately controls, since they can install the app on their own store and capture one of their own real webhook deliveries) remains HMAC-valid when replayed with **forged** `x-shopify-shop-domain` / `x-shopify-topic` headers pointed at a different (victim) shop. `Registry.process` will accept it and hand `WebhookMetadata.new(shop: <victim>, topic: <attacker-chosen>, body: <attacker-chosen>)` to the app's handler.

This is a direct structural analog of the report's bug class: a value used for a security-relevant decision (`unclaimedFlux` accrual in the analog; `shop`/tenant identity here) is not covered by the check meant to authenticate it (`claimableFlux` recompute in the analog; the webhook HMAC here).

### Scope check against the rules

- It's inside `lib/shopify_api/webhooks/**`, not excluded.
- It requires no `api_secret_key` leakage, no access token, no privileged account — just the ability to send an HTTP POST to the app's public webhook endpoint plus one legitimately-signed payload from any shop (including the attacker's own trial/dev shop).
- Impact: cross-tenant data/event injection — a handler that keys off `data.shop` (the documented, intended usage per `docs/usage/webhooks.md`) can be made to process attacker-controlled data as if it belonged to a different merchant. This matches "cross-tenant access" in the Critical impact bucket.

### Title
Webhook shop/topic identity not bound by HMAC allows cross-tenant webhook forgery — (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw body. The `shop-domain` and `topic` headers that `Webhooks::Registry.process` uses to route and label the event to the handler are never part of the HMAC computation, so they carry no authenticity guarantee.

### Finding Description
`Utils::HmacValidator.validate` ( [5](#0-4) ) proves only that the request body was HMAC-signed with the app's (shop-agnostic) `api_secret_key`. `Webhooks::Request#shop`, `#topic`, `#api_version`, and `#webhook_id` ( [2](#0-1) ) come from headers that are outside that signature. `Registry.process` trusts them anyway to build `WebhookMetadata` for the handler ( [3](#0-2) ). Because `api_secret_key` is identical for every shop that installs the app, a valid `(body, hmac)` pair obtained from any one shop (including one the attacker controls) can be replayed with an arbitrary `shop-domain`/`topic` header pair and will still pass validation.

### Impact Explanation
An app handler that trusts `WebhookMetadata#shop` to select the tenant record/access token to act on (the pattern the gem's own docs describe) can be tricked into applying attacker-supplied webhook data to a different merchant's tenant context — a cross-tenant integrity/confidentiality violation reachable by any internet user who can reach the app's public webhook endpoint and has captured one valid signed payload (trivially obtainable by installing the target app on a shop they control).

### Likelihood Explanation
Moderate-to-high: webhook endpoints are public HTTP endpoints by design; obtaining one valid signed payload only requires installing the app once on an attacker-owned development/trial store, which is normal, unprivileged behavior for anyone integrating with a public app.

### Recommendation
Bind the asserted `shop` (and ideally `topic`) into the value that is verified — e.g., require the host application to confirm `request.shop` is a shop with an active installation/session before trusting `WebhookMetadata`, or expand webhook signature verification (where Shopify's payload supports it) to check the header set against the specific shop's own stored secret/session context rather than only the shared `api_secret_key`. At minimum, document prominently that `Registry.process` does not authenticate `shop`/`topic`, and that handlers must independently confirm the shop is a known, currently-installed tenant before acting on payload data.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver one real webhook (e.g. `orders/create`) to the app's public endpoint, capturing the raw body `B` and `X-Shopify-Hmac-Sha256: H`.
2. Attacker crafts a new POST to the same public endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `Webhooks::Request.new` accepts the forged headers; `HmacValidator.validate` succeeds because it only checks `B` against `H` using the shared `api_secret_key` ( [5](#0-4)  and [1](#0-0) ).
4. `Registry.process` dispatches to the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` ( [6](#0-5) ), causing the app to process attacker-chosen data under the victim's tenant identity.

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
