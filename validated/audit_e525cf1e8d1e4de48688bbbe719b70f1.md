### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body. The `shop` (merchant) attribution, which is taken from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, is never included in the signed payload. Any unprivileged user who legitimately installs the app on their own store can capture a validly-signed `(body, hmac)` pair and replay it with a different shop header, causing the app to process the event as if it originated from an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read directly from headers and is not part of the signed content: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC exclusively against `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` trusts this single HMAC check as proof of authenticity for the *entire* request, then forwards the unauthenticated `request.shop` value straight to the app-defined handler: [4](#0-3) 

This is structurally identical to the reported Curve `GaugeController` bug: a value that materially affects downstream state (`_user_weight` there, `shop` here) is *acted upon* by the system but is *not covered* by the integrity check that is supposed to bind the whole message together. In the gauge controller, the check summed `power_used` but didn't lock timing, letting the same weight be reused. Here, the check verifies the body's HMAC but doesn't bind the `shop` header to that same signature, letting the same signed body be reused with an arbitrary shop label.

The equality that should hold — `shop_covered_by_hmac == shop_used_for_handler_dispatch` — is broken: `shop_covered_by_hmac = ∅` (empty set; not included in `to_signable_string`), while `shop_used_for_handler_dispatch = request.shop` (fully attacker-controlled header value).

### Impact Explanation
Any Shopify app built on this gem that relies on `WebhookMetadata#shop` to decide which merchant's records to update (a standard and encouraged pattern, since `Registry.process` passes `shop: request.shop` directly to the handler) can be tricked into applying an attacker's own store data/event to a victim shop's account, or vice versa. This is a cross-tenant integrity violation: the attacker (who legitimately controls only their own shop/installation) can cause a webhook event to be attributed to and processed under a different merchant's identity, without ever needing the app's `client_secret` or any victim credential. This matches the "Critical - cross-tenant access" impact bucket defined in scope.

### Likelihood Explanation
Exploitation requires no privileged access: any internet user can install the target app on their own development/test store (a normal, unprivileged flow), trigger a webhook topic whose body content they can predict or control (e.g., updating a product/order they own to get a specific JSON body), capture the resulting valid `(raw_body, hmac)` pair, and replay it to the app's webhook endpoint with the `shop` header changed to the victim's domain. Because `Registry.process` and `HmacValidator.validate` never bind `shop` into the signature, the forged request passes verification unmodified.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable content, or independently verify that the shop header corresponds to a shop with an active, stored session/installation before dispatching to handlers, rather than trusting `request.shop` merely because the body signature validated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged action).
2. Attacker triggers a webhook (e.g. `orders/create`) with body content they control, and Shopify sends the app a validly HMAC-signed request:
   ```
   headers: {
     "x-shopify-topic" => "orders/create",
     "x-shopify-hmac-sha256" => "<valid_hmac_of_raw_body>",
     "x-shopify-shop-domain" => "attacker-shop.myshopify.com"
   }
   body: "{...attacker-controlled order json...}"
   ```
3. Attacker captures this exact `raw_body` + `hmac` pair (e.g. via a network proxy on their own server that received the webhook).
4. Attacker replays the identical `raw_body`/`hmac` to the app's webhook endpoint, but changes only the shop header:
   ```
   headers: {
     "x-shopify-topic" => "orders/create",
     "x-shopify-hmac-sha256" => "<same_valid_hmac>",   # unchanged - HMAC only covers body
     "x-shopify-shop-domain" => "victim-shop.myshopify.com"
   }
   body: "{...same attacker-controlled json...}"       # unchanged
   ```
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` succeeds, because it only checks `to_signable_string` (the raw body), which is unchanged.
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes attacker-controlled data under the victim shop's identity, as shown by the direct pass-through in `Registry.process`: [5](#0-4)

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
