### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes the tenant identity (`shop`) from an HTTP header that is never included in the HMAC-signed payload. `ShopifyAPI::Webhooks::Registry.process` validates only that the raw request body is authentic, then forwards the unauthenticated `shop` value to the app's handler as the trusted tenant identifier. This breaks the identity binding `shop_verified == shop_used`, allowing a party who has captured any one legitimately-signed webhook body/HMAC pair to relabel it as belonging to an arbitrary target shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly, unauthenticated, from HTTP headers: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the signature strictly over `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it to the `hmac-sha256` header: [4](#0-3) 

`Registry.process` relies on this validation, then immediately trusts `request.shop` as the tenant for the webhook without any further check that it matches what was actually signed: [5](#0-4) 

The gem's own documentation instructs integrators to use `data.shop` as the authoritative shop identifier for routing/persisting webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [6](#0-5) 

Because only the body bytes are authenticated, the binding that should hold — "the `shop` value the app trusts equals the `shop` the signature was computed for" — does not hold. `HmacValidator.validate` proves `raw_body` integrity/origin, but `Registry.process` and `WebhookMetadata` propagate `request.shop`, a value entirely outside the signed material.

### Impact Explanation
An unprivileged party who obtains any single legitimately HMAC-signed `(raw_body, hmac)` pair for the shared app secret (e.g., by controlling their own shop's webhook receiver temporarily and logging Shopify's real callback) can replay that exact body+signature to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` / `shopify-shop-domain` header. `HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to any shop of the attacker's choosing. Any app logic that keys persistence, authorization, or side effects off `data.shop` (as the library's own docs instruct) can be made to attribute attacker-controlled webhook content to a different tenant — a cross-tenant data/trust confusion.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(body, hmac)` pair signed with the app's secret. This is achievable by any merchant/developer who installs the vulnerable app on their own store (a routine, unprivileged action) and captures a webhook Shopify sends them, then replays it toward the app's endpoint with a forged `shop-domain` header. No knowledge of `api_secret_key` or any other credential is required to perform the header substitution itself, only observation of one's own legitimate webhook traffic.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the material that is cryptographically verified, or cross-check the header-derived `shop` against an independent authoritative source (e.g., look up the webhook subscription id server-side and confirm its registered shop matches the header) before invoking the handler. At minimum, document prominently that `data.shop` in `WebhookMetadata` is not cryptographically bound to the signature and must not be used as a sole tenant-authorization signal without additional server-side verification (e.g., matching against `webhook_id` recorded at registration time).

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and temporarily points/observes the app's webhook endpoint (or a proxy) to capture one real Shopify webhook: raw body `B` and header `X-Shopify-Hmac-SHA256: H` (valid for the shared app secret), along with topic `T`.
2. Attacker sends a new HTTP POST to the real app's webhook endpoint with the same raw body `B` and the same `X-Shopify-Hmac-SHA256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic: T`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) , which passes because only `B` is checked against `H`.
4. The registered handler for topic `T` receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and body `B`, even though this data never originated from `victim-shop`, causing the app to process/store attacker-controlled content as `victim-shop`'s data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
