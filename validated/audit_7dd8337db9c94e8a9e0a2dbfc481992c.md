Confirmed: `WebhookMetadata.shop` (lib/shopify_api/webhooks/webhook_handler.rb:6-8) carries `request.shop`, which is a raw, unauthenticated header value, and is handed directly to host-app handlers for tenant attribution.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats `request.shop` as the authenticated tenant identity for a webhook, but `HmacValidator` only verifies the request body — the `shop-domain` header used for tenant attribution is never bound to the HMAC signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it against the `hmac-sha256` header: [2](#0-1) 

`Request#shop`, however, is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, with no relation to the signed body: [3](#0-2) 

`Registry.process` validates only the HMAC, then forwards `request.shop` unchecked as the tenant identity to the app's handler: [4](#0-3) 

That value is placed into `WebhookMetadata.shop`, which the gem's own documentation instructs host apps to use directly as the shop/tenant key (e.g. `perform_later(shop_domain: data.shop, ...)`): [5](#0-4) [6](#0-5) 

**Root cause / broken binding:** the gem implicitly claims `hmac-verified(body) == shop-domain-header-is-genuine`, but the equality that actually holds is only `hmac-verified(body) == body-is-genuine`. The `shop-domain` header is disjoint from what the HMAC covers.

**Exploit path:** an unprivileged attacker who has (or creates) their own Shopify development store and installs the vulnerable app receives genuine, correctly-HMAC-signed webhook deliveries for their own shop from Shopify. Because the app's webhook endpoint is a single shared multi-tenant endpoint (per `docs/usage/webhooks.md` "Process a Webhook" example), the attacker can replay that exact `raw_body` + `hmac-sha256` value to the same endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (only the body is checked), and `Registry.process` calls the handler with `request.shop` equal to the attacker-chosen victim domain — a cross-tenant impersonation.

### Impact Explanation
This breaks the tenant/shop identity boundary the gem is responsible for asserting to host applications: `Critical - cross-tenant access`. Any app that uses `data.shop` (as instructed by the gem's own docs) to key persistence, queue jobs, or trigger per-tenant side effects (e.g., updating order/product data, billing state, or enqueuing background jobs "for" a shop) can be made to act on behalf of, or write data attributed to, a shop the attacker does not control — using only a webhook payload from their own installation.

### Likelihood Explanation
Likelihood is bounded by needing (a) the attacker to run their own install of the target app (any developer can create a free store and install any public/dev app) and (b) the target app's handler to key mutable/sensitive behavior off `data.shop` without any additional verification — which is exactly the pattern the gem's documentation recommends (`docs/usage/webhooks.md` example uses `shop_domain: data.shop` to route background jobs). No access token, `client_secret`, or privileged account is required — only a normal, unprivileged Shopify merchant/developer account and knowledge of the app's public webhook URL.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`api-version`) header into the value that is HMAC-verified, e.g. by including these headers in `to_signable_string`, or by separately validating that the resolved `webhook_id`/shop pair matches Shopify's records via an authenticated follow-up call before invoking the handler. At minimum, document prominently that `data.shop` from `WebhookMetadata` is not cryptographically bound to the HMAC and must not be trusted for tenant attribution without additional verification (e.g., cross-checking against known installed shops).

### Proof of Concept
1. Install the target app (using `shopify_api`) on attacker-controlled store `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) to receive a legitimate `raw_body`, `x-shopify-hmac-sha256`, and `x-shopify-shop-domain: attacker.myshopify.com` from Shopify.
2. Replay the captured request to the same public webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but changing `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks `raw_body` against the unchanged HMAC.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the registered handler with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the request never came from Shopify on behalf of that shop — demonstrating the broken identity binding.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
