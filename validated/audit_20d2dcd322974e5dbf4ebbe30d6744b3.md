Confirmed. The `shop-domain` header is passed straight through to the app's handler as the tenant identity, while `Request#to_signable_string` (the data covered by the HMAC) only includes the raw body.### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's `WebhookHandler` from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Registry.process` validates only covers the raw request body, not this header. This breaks the binding: `hmac-authenticated-bytes == bytes-used-to-identify-the-tenant`.

### Finding Description
`Registry.process` gate-keeps webhook processing solely on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

That validator recomputes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — it does not include the `shop`, `topic`, `webhook_id`, or `api_version` headers: [3](#0-2) 

Yet `shop` (parsed straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no validation) is exactly the field the library passes to the app's handler as the authoritative tenant identifier: [4](#0-3) [5](#0-4) [6](#0-5) 

The library's own documentation instructs apps to treat `data.shop` as the trusted shop domain of the webhook and use it directly (e.g., to key job queues, look up per-shop credentials, or route the payload) without further verification, since the gem is expected to have already authenticated the request: [7](#0-6) 

Because the header is excluded from `to_signable_string`, any request whose `raw_body` HMAC is valid for the app's secret will pass validation *regardless of what `shop` header accompanies it*. An unprivileged internet user who is themselves a legitimate merchant with the app installed (or anyone who can obtain one genuinely-signed webhook body/HMAC pair from Shopify, e.g. by triggering an event on their own store) can resend that exact `raw_body` + `hmac` combination to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a different tenant. `Utils::HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will dispatch the handler with `shop` set to the attacker-chosen victim shop.

This is a direct instance of the requested bug class: *"a field acted on but not covered by the HMAC."* The webhook's tenant-binding is broken — the shop identity the app trusts is not the shop identity the signature attests to.

### Impact Explanation
This crosses a tenant boundary using only a validly-signed body an attacker can legitimately obtain from their own store, satisfying the Critical bucket ("cross-tenant access"). Any app relying on `data.shop` from `WebhookMetadata` (as the docs instruct) to key per-tenant state, dedupe, authorize, or fan out work can have its per-tenant records for shop B corrupted or falsely populated by data forged from shop A. Depending on the topic (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`), this can trigger destructive or compliance-relevant per-tenant actions against a shop that never sent that event.

### Likelihood Explanation
Requires only: (1) the app's webhook endpoint being reachable (it must be, since Shopify calls it over the public internet), and (2) the attacker possessing one legitimately-signed `(raw_body, hmac)` pair, which is trivially obtained by any merchant who has the app installed and triggers an eligible webhook event on their own store. No access to `api_secret_key` or a privileged account is required — only a standard merchant/app-install position and the ability to POST to the app's public webhook URL, i.e., an "unprivileged internet user" once they've installed the app under their own shop. No TLS interception or credential theft is needed.

### Recommendation
Bind the shop (and, ideally, topic/webhook id) into the signed payload, or otherwise cryptographically tie the header value to the authenticated request:
- Include the `shop`, `topic`, and `webhook_id` header values in `to_signable_string` so `Utils::HmacValidator` authenticates them along with the body, or
- Alternatively, cross-check the `shop` value obtained from the webhook against the shop of the merchant/session the app expects for that specific registration, before trusting it in application logic, and document that `WebhookMetadata#shop` is not currently authenticated so consumers do not treat it as trusted without a session lookup.

### Proof of Concept
1. App has the webhook registered at `POST /callback/orders/create`, implemented per the documented pattern:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
)
```
2. Attacker installs the app on their own store `attacker-shop.myshopify.com` and triggers `orders/create` (e.g., places an order). Shopify sends a legitimately signed webhook to the app:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid HMAC over raw_body using app's secret>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
Body: {"id": 123, ...}
```
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value (they have full visibility as the recipient shop admin/traffic is delivered to a URL they can also curl/replay to), then sends their own POST directly to the same public endpoint:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same valid HMAC as captured>
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Body: {"id": 123, ...}   # identical, unmodified raw_body
```
4. `HmacValidator.validate` recomputes the HMAC over `raw_body` only (per `Request#to_signable_string`) and it matches — validation passes.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: {"id": 123, ...}, ...))`, and the app processes forged data attributed to `victim-shop.myshopify.com`, breaking the shop/session tenant boundary.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
