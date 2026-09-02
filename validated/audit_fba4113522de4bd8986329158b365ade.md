This confirms the finding: `docs/usage/webhooks.md` explicitly documents `data.shop` as "The shop domain of the webhook" — a value the host app is expected to trust and use (e.g. for looking up the session/store record), yet this value is sourced purely from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header and is never included in the HMAC-covered content.

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) attributes from raw, unauthenticated HTTP headers, but the HMAC signature verified by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body. This breaks the intended binding `hmac == HMAC(secret, body + shop)`; in reality the gem only enforces `hmac == HMAC(secret, body)`, letting an attacker who controls one legitimately-signed webhook rewrite the `shop` field freely while still passing signature validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers without any cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature strictly over `to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` validates only this body HMAC, then immediately trusts `request.shop` and forwards it, unverified, to the app's handler: [4](#0-3) 

The gem's own documentation instructs app developers to treat `data.shop` as the authoritative shop identity for the webhook (e.g. to route/store data per-tenant), reinforcing that this field is meant to be trusted: [5](#0-4) 

Because `shop` is never included in the signed content, the identity binding `authenticated_body == shop_attributed_to_that_body` does not hold. Any entity that can obtain one genuinely Shopify-signed webhook (which every merchant installing the app can, for their own shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` passes the attacker-chosen `shop` straight to the handler as if Shopify had asserted it.

### Impact Explanation
This is a cross-tenant identity-binding break: the merchant/attacker for shop A can cause the app to process webhook content while asserting it belongs to shop B (a different tenant they do not control). Since host applications are explicitly told by this gem's documentation to key their per-shop logic off `data.shop`, this can be used to inject or misattribute data into another tenant's account context (e.g., forged `orders/create`, `app/uninstalled`, or other topic payloads attributed to a victim shop), a cross-tenant access impact.

### Likelihood Explanation
Likelihood is limited by the fact the attacker can only replay whatever body content Shopify actually signed for their own shop (they cannot forge arbitrary JSON, since they don't know `api_secret_key`). However, mounting the attack requires only installing the app on an attacker-controlled shop, capturing one legitimate webhook delivery, and replaying it with a modified header to the app's public webhook endpoint — no special privileges beyond a normal merchant account.

### Recommendation
Bind the trusted request metadata (`shop`, `topic`) into the value verified by the HMAC, e.g. by incorporating the relevant Shopify headers into `to_signable_string`/validation, or by cross-checking `request.shop` against the shop associated with the specific webhook subscription (`webhook_id`) before invoking the handler, rather than trusting the unauthenticated header value outright.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures a webhook subscription (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical body `B` and HMAC header to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `B` only, matches the header, and returns `true`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` and invokes the app's handler, which processes/persists `B` under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
