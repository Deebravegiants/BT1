### Title
Webhook shop-domain is not covered by the HMAC signature, allowing tenant-spoofed webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the shop-identifying header (`x-shopify-shop-domain`) is read separately and is never included in the signed content. `Registry.process` trusts this unauthenticated `shop` value and hands it straight to the app's webhook handler as the tenant key, even though the library's own documentation states that `process` "will verify the request did indeed come from Shopify."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header independently of the signed content: [2](#0-1) 

`HmacValidator.validate` computes the comparison signature strictly over `verifiable_query.to_signable_string`, i.e. the raw body, and never incorporates the shop header: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC passes, then forwards the unauthenticated `request.shop` value to the handler as `WebhookMetadata.shop`: [4](#0-3) 

The library's own docs instruct apps to use `data.shop` as the tenant/shop key for storing or dispatching the webhook payload (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), and describe `process` as verifying "the request did indeed come from Shopify": [5](#0-4) [6](#0-5) 

The binding that should hold is:
`shop attributed to processed webhook (WebhookMetadata.shop) == shop whose merchant/app secret produced the valid HMAC`

Because the shop header is excluded from `to_signable_string`, this equality is not enforced: any `(raw_body, valid_hmac)` pair legitimately observed from one shop's webhook delivery (the app's `client_secret`/HMAC secret is shared across all shops that install the app) remains valid HMAC-wise if replayed with an arbitrary, attacker-chosen `x-shopify-shop-domain` header. `Registry.process` will accept it and dispatch it to the handler labelled with the attacker-chosen shop.

### Impact Explanation
Any app that follows the documented pattern of using `data.shop` as the tenant key (session lookup, DB partition key, job dispatch, etc.) can have webhook events forged and attributed to a victim shop the attacker does not control. This is a cross-tenant data injection: an attacker who has observed one valid signed webhook body/HMAC pair (e.g. from a shop they installed the app on themselves) can cause the app to process/store that payload under a different, victim shop's identity, since the shop is not part of the authenticated content. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs to capture a single legitimately-signed webhook (raw body + HMAC) — which requires nothing more than being a normal, unprivileged app user/merchant (e.g. installing the app on any store and triggering an event) — and then replay it to the app's public webhook endpoint with a modified `shop-domain` header. No access token, `client_secret`, or privileged access is required, matching the required threat model.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-verifiable content, or otherwise cryptographically bind the `shop-domain` header to the signed request before it is trusted as the tenant identifier in `WebhookMetadata`. At minimum, `Registry.process`/`Request` should not present `shop` as verified data unless it is actually covered by the signature, and documentation should be corrected to avoid implying full request authenticity when only the body is verified.

### Proof of Concept
1. Install/register the target app on Shop A (attacker-controlled) and receive a legitimate webhook delivery for topic `orders/create`, capturing `raw_body` and the `x-shopify-hmac-sha256` header. This HMAC is valid because it's computed with the app's shared `client_secret` over `raw_body` only (`Request#to_signable_string`).
2. Replay the exact same `raw_body`/`x-shopify-hmac-sha256` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb#validate_signature`) still succeeds because the shop header was never part of the signed string.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb#process`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches it to the app's handler, which per the documented usage pattern treats `data.shop` as the trusted tenant key — resulting in attacker-controlled data being processed/stored under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L20-27)
```markdown
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
