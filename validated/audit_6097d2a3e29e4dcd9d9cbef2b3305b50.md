The webhook request handling in this gem has an identity-binding gap between what the HMAC verifies and what the library hands to app handlers as the authenticated tenant identity.

### Title
Webhook shop-domain identity is not covered by HMAC verification, enabling cross-tenant webhook data injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` documents that it "will verify the request did indeed come from Shopify" before dispatching to the app's handler [1](#0-0) , and the handler receives a `shop` field described simply as "The shop domain of the webhook" [2](#0-1) . In reality, only the raw request body is covered by the HMAC signature; the `shop` (and `topic`, `webhook_id`, `api_version`) values come from HTTP headers that are excluded from the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside that signable string: [4](#0-3) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` and secure-compares it to the `hmac` header: [5](#0-4) 

`Registry.process` uses this validation as its sole authenticity check, then immediately trusts `request.shop` as the tenant identity forwarded to the app's handler: [6](#0-5) 

Because the shop header is never part of the signed bytes, the binding `HMAC-verified bytes == identity used by handler` does not hold: `hmac` verifies `raw_body` only, while `shop` (the tenant key the app will act on) is taken from an unauthenticated header. Any legitimately-signed webhook (e.g. one Shopify sends for a shop the attacker themselves controls/installed the app on) can be replayed to the app's public webhook endpoint with the `shop-domain` header swapped to a victim shop, and it will still pass `HmacValidator.validate` because the signature never covered that header.

### Impact Explanation
This breaks the tenant/shop identity binding that the library's documentation implies is guaranteed by "verifying the request came from Shopify." An attacker who owns any shop with the app installed can capture a validly-signed webhook body/HMAC pair from their own store's events, then POST it directly to the app's public webhook callback URL with an arbitrary victim `shop-domain` header. `Registry.process` will accept it as authentic and dispatch attacker-controlled body content labeled with the victim's shop to the app's handler, which per the documented contract will act on it as if Shopify sent it for that victim — a cross-tenant data injection into the victim's records.

### Likelihood Explanation
Webhook callback URLs are necessarily public HTTP endpoints reachable by anyone, and obtaining one genuinely-signed webhook for an attacker-controlled shop only requires installing the target app on a shop the attacker controls (no `api_secret_key` or privileged access needed). Constructing the replay request requires only copying body+HMAC and substituting the shop header, which is straightforward for any host app that follows the documented `process` usage exactly as shown in `docs/usage/webhooks.md`.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed content the HMAC validator checks, or otherwise cryptographically tie the header-derived shop to the signature (e.g., include it in `to_signable_string`, or cross-check it against a shop registered/expected for that webhook subscription) before it is handed to `WebhookMetadata`/the app handler.

### Proof of Concept
1. Attacker installs the target app on `evil-shop.myshopify.com` and triggers an event (e.g. `orders/create`), capturing the resulting POST Shopify sends to the app's webhook endpoint, including `x-shopify-hmac-sha256: <valid_hmac>` and body `B`.
2. Attacker sends a new POST to the same public webhook endpoint with the identical body `B` and `x-shopify-hmac-sha256` header, but with `x-shopify-shop-domain` changed to `victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes the HMAC over `B` only (`request.rb` `to_signable_string`) and it matches, so `Registry.process` proceeds and calls the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, even though this event never occurred on the victim's shop.

### Citations

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
