### Title
Webhook shop identity is not bound to the HMAC-verified payload, enabling cross-tenant impersonation via webhook replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only the raw request body against the `hmac-sha256` header, but the `shop-domain` header — which the gem's documentation explicitly tells host apps to trust as the tenant identifier (`data.shop`) — is never covered by that HMAC. This breaks the identity binding "shop authenticated by the HMAC" == "shop trusted for the event," the same class of bug as the referenced report, where one balance/identity check (`recoverTokens` on `depositToken`) was performed on bytes that also covered another identity's state (`rewardToken`), letting the creator drain funds belonging to the wrong bucket.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate_signature` computes the HMAC exclusively over that signable string and compares it to the `hmac` accessor, which itself is parsed straight from the `hmac-sha256` header: [2](#0-1) [3](#0-2) 

`request.shop` is read directly from the `shop-domain` header, entirely outside the HMAC computation: [4](#0-3) 

`Registry.process` validates the HMAC and then forwards `request.shop` unchanged to the app's handler as the trusted tenant identifier: [5](#0-4) 

The gem's own documentation instructs host apps to treat `data.shop` as "The shop domain of the webhook" and to key downstream processing on it directly: [6](#0-5) 

Since the app's `api_secret_key` is shared across every shop that installs the app, any merchant who installs the app can capture a genuine, validly-HMAC'd webhook body from their own store (Shop A), then replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header to name a different victim shop (Shop B). `HmacValidator.validate` still passes because it never inspects the shop header, so `Registry.process` calls the handler with `shop: "Shop B"` even though the payload actually originated from, and was signed for, Shop A.

### Impact Explanation
This is a cross-tenant identity-binding break: the value checked by the cryptographic proof (raw body bytes) is not the value the API surfaces as the authenticated tenant (`shop-domain` header). Any app that follows the gem's documented pattern of using `data.shop` to select which merchant's records to update (exactly as shown in the gem's own example) can be made to attribute or apply another shop's real webhook event to an arbitrary victim shop of the attacker's choosing — a cross-tenant access primitive satisfying the Critical impact bar.

### Likelihood Explanation
The prerequisite is only that the attacker controls one legitimate installation of the target app (an "unprivileged internet user" from the perspective of any other merchant) and can capture one real webhook delivery from their own store — no access to `api_secret_key`, access tokens, or other shops' credentials is required. Every subsequent replay against any registered webhook path is a simple HTTP request with a forged header.

### Recommendation
Include the shop identifier (and ideally topic/webhook-id) in the HMAC-covered signable content, or otherwise cryptographically bind the `shop-domain` header to the verified body (e.g., by having `Registry.process` re-derive/validate the shop against a per-shop registered webhook record instead of trusting the unauthenticated header verbatim). At minimum, document prominently that `data.shop` is not authenticated by the HMAC and must not be trusted for tenant-scoping decisions without additional verification (e.g., matching against an expected/registered shop for that webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify — both valid because they were genuinely signed by the app's shared `api_secret_key`.
2. Attacker replays this exact `(raw_body, hmac)` pair to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only and succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop == "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`, `lib/shopify_api/webhooks/request.rb:20-23`).
5. The host application's handler, following the gem's documented pattern, processes the (attacker-controlled) event body as belonging to `victim.myshopify.com`, achieving cross-tenant data injection/impersonation.

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

**File:** docs/usage/webhooks.md (L10-29)
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
