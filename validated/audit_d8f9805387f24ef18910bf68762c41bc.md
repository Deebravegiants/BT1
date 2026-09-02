Confirmed: `Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), and `Request#shop` is read straight from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header (`lib/shopify_api/webhooks/request.rb:20-23`). `Registry.process` validates HMAC only over the body, then hands `request.shop` straight into `WebhookMetadata` for the handler (`lib/shopify_api/webhooks/registry.rb:189-199`), and the docs explicitly tell app developers to key their per-shop logic off `data.shop` (`docs/usage/webhooks.md:12-26`). This confirms the binding break I'll report.

### Title
Webhook shop attribution is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/exposes the HMAC signature over the raw body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are taken verbatim from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, so the "shop this webhook is about" is never actually bound to the signature that proves the payload's authenticity.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature by calling `verifiable_query.to_signable_string` and comparing it against the `hmac` header: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body, never any headers: [2](#0-1) 

Meanwhile `Request#shop` is read straight out of the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with no cryptographic binding to that header's value: [3](#0-2) 

`Registry.process` validates the HMAC (over body only) and then immediately trusts `request.shop` to construct the object delivered to the app's handler: [4](#0-3) 

The gem's own documentation instructs developers to key shop-specific logic (session lookup, per-tenant enqueue, etc.) directly off `data.shop`: [5](#0-4) 

The broken identity binding is:
`shop authenticated by HMAC (none — HMAC only covers body bytes) ≠ shop acted upon by the handler (request.shop, an unauthenticated header value)`

Because Shopify's real webhook HMAC (computed with the app's shared `client_secret`) only signs the body, any attacker who can obtain one legitimate `(body, hmac)` pair — for example by triggering an identical-body webhook event on their own shop, or from a body whose bytes they control/predict — can replay that exact body+hmac pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The HMAC check in `HmacValidator.validate` passes because it never inspects the header, so the forged shop attribution reaches the handler as if it were authentic.

### Impact Explanation
This breaks the cross-tenant boundary the HMAC is meant to guarantee: an app relying on the documented `data.shop` field to determine which merchant's data/session the payload belongs to can be made to act on attacker-supplied or replayed body content while attributing it to a victim shop (or vice versa), since the header carrying the shop identity is entirely unauthenticated. This falls under cross-tenant access resulting from a field (the shop attribution) that is acted upon by the host application but not covered by the HMAC that is supposed to authenticate the whole request.

### Likelihood Explanation
Exploitability requires the attacker to have obtained at least one genuine `(raw_body, hmac)` pair from Shopify — most straightforwardly by being (or controlling) a merchant of the app who can trigger a webhook with body content they choose or predict (e.g. a webhook whose body is deterministic or attacker-influenced, or simply reusing their own shop's webhook and re-pointing it at another shop's identifier). No access to `api_secret_key` or any credential belonging to the app or the victim is needed — only observation of one legitimate webhook delivery, which any merchant installing the app can obtain for their own store.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string that is HMAC-verified, or otherwise cryptographically bind the `shop` value to the verified payload before constructing `WebhookMetadata`, so that a valid HMAC can only be produced for the exact shop it was generated for.

### Proof of Concept
1. App merchant A installs the app and triggers a webhook event whose body is fixed/predictable (e.g. an empty or attacker-crafted JSON body if the topic allows it), capturing the resulting `x-shopify-hmac-sha256` header value `H` for body `B`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with `raw_body = B`, `x-shopify-hmac-sha256 = H`, but `x-shopify-shop-domain = victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(client_secret, B) == H` — the shop header is never part of the signed string (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and, following the gem's documented pattern, performs shop-scoped work (session lookup, per-tenant job enqueue) against the victim shop using attacker-influenced body content.

### Citations

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

**File:** docs/usage/webhooks.md (L10-26)
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
```
