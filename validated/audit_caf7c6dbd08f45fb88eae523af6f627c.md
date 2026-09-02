### Title
Webhook `shop`/`topic` attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator` authenticates *nothing but the body bytes*. The `shop-domain`, `topic`, `webhook-id` and `api-version` headers are read straight from the incoming HTTP request and passed to the handler unauthenticated. This mirrors the reported bug class: a field that is *acted on* (`shop`) is not covered by the *verified bytes* (HMAC over body only).

### Finding Description
`Request#to_signable_string` is defined as simply the raw request body: [1](#0-0) 

`HmacValidator` computes and compares the HMAC only over that signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` / `request.topic` (which come directly from HTTP headers, not from the signed payload) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`Request#shop`/`#topic` are read from the `shopify-shop-domain`/`shopify-topic` (or `x-shopify-*`) headers with no cryptographic binding to the signature: [4](#0-3) 

**Broken identity binding (as an equality the gem should enforce but does not):**
`hmac_valid(body)` should imply `shop_header == shop_that_Shopify_actually_sent_this_body_for`. In reality `hmac_valid(body)` only proves the body bytes were produced by a holder of the app's `api_secret_key` (i.e., genuinely came from Shopify for *some* webhook delivery) — it says nothing about which shop or topic accompanied that body. `request.shop` / `request.topic` can be swapped by anyone who can reach the app's public webhook endpoint, without invalidating `request.hmac`.

### Impact Explanation
An unprivileged internet user who operates their own (non-victim) shop can install the target app, trigger any webhook event on their own store, and capture the genuine `(raw_body, hmac)` pair Shopify sends (this requires no `api_secret_key`, access token, or privileged access — installing an app and firing a webhook is standard merchant behaviour). They can then replay that exact body+HMAC directly to the app's public webhook receiver URL while substituting the `shopify-shop-domain` header (and/or `shopify-topic`) with an arbitrary victim shop domain. `Registry.process` will validate the HMAC successfully (only the body is checked) and dispatch the handler with `shop: "victim-shop.myshopify.com"`. Any app that relies on `WebhookMetadata#shop` to determine which tenant's data to create, update, or delete — which is the gem's own documented usage pattern — will attribute attacker-controlled payload data to a shop the attacker does not own. This is cross-tenant data injection/corruption achieved entirely through this gem's verification primitives, not through the host app ignoring the documented API.

### Likelihood Explanation
High. Obtaining one valid `(body, hmac)` pair requires nothing more than installing the app on any store and causing one webhook delivery — an action any internet user can perform on their own tenant. Forging headers on a direct HTTP POST to a publicly reachable webhook endpoint requires no special access, no secrets, and no interaction with a victim.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` (in addition to the body) in the HMAC-signed material used by `to_signable_string`, or otherwise cryptographically bind these header values before they are attached to `WebhookMetadata`. At minimum, document and warn that `request.shop`/`request.topic` are unauthenticated and must not be trusted for tenant attribution without an out-of-band verification (e.g., cross-checking against the shop the webhook was registered for).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) to capture a genuine `(raw_body="{...}", hmac=H)` pair signed by the real `api_secret_key`.
2. POST directly to the app's webhook endpoint with:
   - Body: the captured `raw_body`
   - `shopify-hmac-sha256`: the captured `H`
   - `shopify-shop-domain`: `victim-shop.myshopify.com` (attacker-chosen)
   - `shopify-topic`: unchanged or attacker-chosen registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only recomputes HMAC over `raw_body` and succeeds: [3](#0-2) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, even though Shopify never sent this data for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
