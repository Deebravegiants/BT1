### Title
Webhook `shop` field is unauthenticated (not covered by HMAC), enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop` header value straight to the app's handler as the tenant identifier — without that value ever being part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`; the `shop` (and `topic`, `webhook_id`, `api_version`) headers are excluded from the signable string. [1](#0-0) 
`Utils::HmacValidator.validate` computes/compares the HMAC only against `verifiable_query.to_signable_string`, i.e. the raw body bytes. [2](#0-1) 
`Registry.process` checks `Utils::HmacValidator.validate(request)` and, once it passes, builds `WebhookMetadata` directly from `request.shop`, which is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cross-check against the body or against any known/installed shop. [3](#0-2) [4](#0-3) 

The binding that should hold is: `shop used for tenant routing == shop cryptographically bound to the payload`. In this implementation that equality does not hold — the HMAC only proves "bytes verified" (the raw body) while the tenant identity ("bytes parsed" as `shop`) is taken from an unauthenticated header. Because the webhook secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is shared across every shop that installs the same app, any merchant who legitimately installs the app can capture a validly-signed webhook body Shopify sends them for their own store, then replay that exact body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. The HMAC check still passes (it never inspected the header), and `Registry.process` calls the handler with `data.shop` set to the attacker-chosen victim shop while `data.body` is the attacker's own (otherwise legitimate) payload.

The gem's own documentation instructs integrators to trust `data.shop` as the tenant key exactly this way, so an app following the documented pattern is directly exposed: [5](#0-4) 

### Impact Explanation
This breaks the tenant boundary that host applications rely on to route webhook data to the correct merchant record (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)` as shown in the docs). An attacker who is merely an ordinary merchant with the app installed can inject data attributed to another shop into the host application's processing pipeline for any shop, i.e. cross-tenant data confusion/injection using only their own valid app installation — no access token, no `client_secret`, and no privileged account required.

### Likelihood Explanation
Moderate-to-high: exploitation only requires installing the app as an unprivileged merchant (something any attacker can do for public apps), capturing one legitimate webhook delivery, and replaying it with a modified header — no cryptographic material needs to be forged since the header is simply not covered by the signature.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) fields in the signable string used for HMAC verification, or otherwise cryptographically bind the shop identity to the payload before it is trusted by `Registry.process`/`WebhookMetadata`. Alternatively, document explicitly that `data.shop` is not authenticated and must be cross-validated by host apps against a known/installed-shop list before use.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; receive a real webhook delivery with a valid `x-shopify-hmac-sha256` for some `raw_body` (e.g. an `orders/create` payload).
2. Replay the exact `raw_body` and `x-shopify-hmac-sha256` header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC. [6](#0-5) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's own webhook body>, ...)`, and any host app following the documented pattern will process/store this as data belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
