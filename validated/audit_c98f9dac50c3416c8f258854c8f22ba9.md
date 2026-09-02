### Title
`Registry.process()` trusts the unauthenticated `shop-domain` header when identifying the tenant for a webhook whose HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook exclusively via `Utils::HmacValidator.validate`, which signs and compares only `Request#to_signable_string` (the raw HTTP body). The `shop` value passed on to the app's handler through `WebhookMetadata` is taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed material. This breaks the intended binding `hmac == HMAC(secret, body ‖ shop)`; in this implementation it is only `hmac == HMAC(secret, body)`.

### Finding Description
`Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`Request#shop` is parsed straight from the header with no cryptographic linkage to the HMAC: [2](#0-1) 

`HmacValidator.validate_signature` recomputes the signature only from `to_signable_string` (the body) and compares it to the received `hmac`: [3](#0-2) 

`Registry.process` gates entirely on this HMAC check and then forwards the header-derived `request.shop` to the app's handler as authenticated tenant identity: [4](#0-3) 

The `shop` field is documented as trustworthy tenant data for the handler to act on (e.g., to key jobs/session lookups): [5](#0-4) 

Because the app-wide `client_secret`/`api_secret_key` is identical across all shops that installed the app (it is not shop-scoped), any holder of one valid `(raw_body, hmac)` pair from a webhook delivered for *their own* shop can replay that exact body with a substituted `x-shopify-shop-domain` header claiming to be a different shop. `HmacValidator.validate` will still return `true`, because the header is outside the signed content, and `Registry.process` will hand the handler a `WebhookMetadata` with `shop` set to the attacker-chosen value.

### Impact Explanation
This is a cross-tenant identity-binding break: the equality the gem is supposed to enforce, `hmac == HMAC(secret, body + shop)`, is reduced to `hmac == HMAC(secret, body)`, so `shop` is verified-adjacent but not covered by the HMAC. Any application relying on `WebhookMetadata#shop` (as recommended in the gem's own docs) to route data or trigger per-tenant side effects can be made to attribute an attacker-controlled shop domain, enabling cross-tenant data confusion/injection — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only unprivileged internet access: an attacker who installs the target app on their own (attacker-controlled) shop can legitimately receive one webhook delivery with a valid `(body, hmac)` pair (using the app's shared `client_secret`, not leaked, since the attacker is a legitimate installer of their own shop), then replay the same body to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header. No secrets need to be exfiltrated; the gem's own verification code accepts the forged request.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header value in the bytes that are HMAC-verified, or otherwise cryptographically bind `shop` to the signature before trusting it in `WebhookMetadata`, e.g., by having `to_signable_string` return a canonical concatenation of the raw body and the relevant headers, and updating `HmacValidator` accordingly.

### Proof of Concept
1. Register the target app on an attacker-controlled shop (`attacker.myshopify.com`) and capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Replay a POST to the app's webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation succeeds [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` [7](#0-6) , even though the body content actually belongs to the attacker's own shop, demonstrating the shop field is accepted without being covered by the HMAC.

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
