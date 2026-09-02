Based on the code, I've confirmed the analog vulnerability class: an identity field (`shop`) is trusted and acted upon by the application, but it is not covered by the HMAC that authenticates the webhook request.

### Title
Webhook `shop-domain` header is trusted for tenant identification but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes/exposes the HMAC-authenticated identity of an incoming webhook using only the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` fields that the application uses to route and process the event are read directly from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` and compares it against the HMAC header: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is **not part of the signed payload**: [3](#0-2) 

This is precisely a "field acted on but not covered by the HMAC" binding break: the equality the code implicitly assumes is
`hmac_valid(raw_body) == shop_header_is_authentic`,
but in reality `hmac_valid(raw_body)` only proves the body bytes were signed by someone possessing the app's `client_secret`; it proves nothing about which shop domain header accompanied that body. `Registry.process` then hands `request.shop` straight to the app's handler as trusted tenant identity: [4](#0-3) 

Because a single app installation (single `api_secret_key`/`client_secret`) issues webhooks for many different merchant shops, and the HMAC secret is the same across all of that app's shops, any legitimate webhook the app receives for **any one of its installed shops** (which an attacker can obtain by being a merchant who installs the app, or by controlling a dev/test store using the app) yields a `(raw_body, hmac)` pair that is valid under the shared secret regardless of which `shop-domain` header is attached. An attacker can replay that valid body+HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim merchant's shop domain. `HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will dispatch to the handler with `WebhookMetadata.new(... shop: request.shop ...)` claiming to be the victim shop.

### Impact Explanation
This breaks the tenant identity binding the whole webhook system is built on: the HMAC is meant to prove "this event genuinely originates from Shopify for shop X," but shop X is never actually covered by the signature. Any application logic that keys off `WebhookMetadata#shop` (e.g., looking up the merchant's session/access token, updating per-shop data, processing `shop/redact` or `customers/data_request` GDPR webhooks, billing/subscription state) can be made to act on a victim's shop identity using data controlled by the attacker's own shop. This is a cross-tenant confusion vulnerability with High impact per the defined criteria.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(raw_body, hmac)` pair from the same app (trivially available to anyone who installs the app on their own store, since the HMAC secret is the app's shared `client_secret`, not per-shop), and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header — both are within reach of an unprivileged internet user/merchant.

### Recommendation
Bind the shop domain (and ideally topic/webhook-id) into the value that is HMAC-verified, or otherwise cryptographically tie the header claims to the signed body — e.g., include the normalized header values in `to_signable_string`, or independently verify `request.shop` against an authenticated source (such as the shop associated with the session/access token used to register that specific webhook subscription) before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com`, causing Shopify to deliver a legitimate webhook (e.g., `customers/data_request`) with body `B` and header `x-shopify-hmac-sha256: HMAC(B, secret)`.
2. Attacker captures `B` and the HMAC header value.
3. Attacker sends a POST to the app's webhook endpoint with body `B`, the captured HMAC header, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks `B` against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches the handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

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
