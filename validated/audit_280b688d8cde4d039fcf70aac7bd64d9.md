This confirms the vulnerability. The gem's own documentation and `Registry.process` implementation establish exactly this pattern: HMAC signs only `raw_body`, while `shop` (the tenant identifier passed to the handler) comes from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, which is never included in the signable string.

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an HTTP header that is excluded from the HMAC-signed payload, while `ShopifyAPI::Webhooks::Registry.process` trusts that unauthenticated `shop` value to build the `WebhookMetadata` passed to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header via `shopify_header` [2](#0-1) . `Registry.process` validates the HMAC over that same signable string only (`Utils::HmacValidator.validate(request)`), then immediately trusts `request.shop` to construct the `WebhookMetadata` delivered to the app's handler [3](#0-2) . `Utils::HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. the raw body, with no knowledge of the shop header [4](#0-3) .

The broken identity equality is:
`bytes verified by HMAC (raw_body)` ≠ `bytes trusted as tenant identity (shop-domain header)`

Because the header is never part of the signed material, any request whose body+HMAC pair was legitimately produced by Shopify for shop A can be replayed with the `shop-domain` header rewritten to shop B, and `HmacValidator.validate` will still return `true` — the app's handler will then process attacker-supplied/replayed body content under a different shop's identity.

### Impact Explanation
This is a cross-tenant access vulnerability. Any user who is a merchant on their own store (an "unprivileged internet user" with respect to other tenants) can trigger legitimate webhooks for their own shop (e.g. `orders/create`), capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair — both of which they can observe on their own webhook endpoint or via any request-capturing proxy — and then submit that exact body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. `Registry.process` reports `Utils::HmacValidator.validate` as passing (since it only checks `raw_body`), and the handler in the host app receives `data.shop == "victim-shop.myshopify.com"` together with the attacker's forged body, matching the documented handler contract in `docs/usage/webhooks.md` [5](#0-4) . Any app that uses `data.shop` (as documented) to select which tenant's records to create/update is exposed to cross-tenant data corruption/injection driven entirely by an attacker-controlled shop that they legitimately own.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented `WebhookHandler`/`Registry.process` pattern exactly as shown in the docs. The attacker needs no secrets — only a Shopify development/partner store of their own (trivial to obtain) to legitimately receive a signed webhook, then a simple HTTP replay with one header changed. No signature bypass or cryptographic weakness is required; the header is architecturally outside the signed scope.

### Recommendation
Bind the shop identity into the signature verification, not just the body. At minimum, require and separately validate `shop-domain` against the tenant that Shopify's Admin API confirms owns the associated `webhook_id`/subscription, or include the shop domain in the string that is HMAC-verified before trusting `request.shop`. Until then, apps built on this gem's documented pattern should be warned in `docs/usage/webhooks.md` that `data.shop` is not covered by the HMAC and must not be trusted for tenant-scoping decisions without an independent authenticated lookup (e.g., resolving the shop via the `webhook_id` through the Admin API instead of the header).

### Proof of Concept
1. Attacker installs the target app on their own development store `attacker.myshopify.com` and subscribes it to `orders/create`.
2. Attacker creates an order, causing Shopify to POST a legitimately signed webhook to the app: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` and replays the exact same POST to the app's webhook endpoint, only changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Request#to_signable_string` still returns `B`; `Utils::HmacValidator.validate` recomputes HMAC over `B` and compares to `H` — this still matches because neither depends on the shop header [6](#0-5) [7](#0-6) .
5. `Registry.process` accepts the request and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed B, ...))` [8](#0-7) , causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
```
