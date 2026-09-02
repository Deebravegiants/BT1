### Title
Webhook `shop-domain` Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute (and `topic`, `webhook_id`, `api_version`) from raw, unauthenticated HTTP headers, while the HMAC signature that `Registry.process` relies on to prove authenticity only covers the raw request body. This breaks the identity binding `hmac_signed_bytes == acted_upon_shop`, letting anyone who can capture one legitimately-signed webhook (e.g., by installing the app on a shop they control) replay it against the same public endpoint with a forged `shop-domain` header pointing at a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated headers: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC matches `verifiable_query.to_signable_string` (i.e., the body), never the headers: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof the whole request — including `request.shop` — is authentic, and forwards `request.shop` directly to the handler: [4](#0-3) 

The gem's own documentation reinforces this false assumption, stating that `Registry.process` "will verify the request did indeed come from Shopify" and that host apps should route/attribute data using `data.shop`: [5](#0-4) [6](#0-5) 

Because the header is not bound to the signed bytes, an unprivileged internet user who owns any shop that installs the app can:
1. Trigger a real webhook event on their own shop, obtaining a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair signed by Shopify with the app's `api_secret_key`.
2. Replay that exact body/HMAC pair to the app's public webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `HmacValidator.validate` still passes (it never inspected the header), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled-content>, ...)`.

This is exactly the "field acted on but not covered by the HMAC" analog: the equality `hmac_verified(body) == shop_attributed(header)` does not hold, and the gem provides no mechanism to detect the mismatch.

### Impact Explanation
Since host applications are told to key their data store lookups off `data.shop` (as shown in the gem's own webhook doc example), an attacker can inject attacker-controlled webhook payloads that get attributed to a shop/tenant they do not own and have no access to. This is a cross-tenant data-integrity/confusion vulnerability: a malicious merchant can poison another merchant's data pipeline (e.g., fake `orders/create`, `app/uninstalled`, or `shop/update` events) purely by owning a free/dev install of the app, satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Any user can install a public/dev version of an app on a shop they control (no privileged credentials needed), trigger any subscribed webhook topic on that shop, and capture the resulting HTTP request their own server receives — this is just normal traffic to their own endpoint. Modifying and replaying the header requires no cryptographic material, only rewriting an unsigned HTTP header. The webhook endpoint is by design a public, unauthenticated HTTP endpoint, so likelihood of exploitation is realistic for anyone motivated to target other merchants using the same app.

### Recommendation
Bind the shop identity to the signed payload rather than trusting the header in isolation:
- Include `shop-domain` (and ideally `topic`/`webhook_id`) in the HMAC-signed material, mirroring `to_signable_string` in `AuthQuery` which signs all relevant fields, or
- Cross-validate the header-derived shop against a shop identifier embedded in the verified JSON body (when the topic's payload includes one), or
- At minimum, document and enforce that host applications must not trust `WebhookMetadata#shop` for authorization/routing decisions without an independent, out-of-band confirmation (e.g., checking against the shop that was expected to receive this specific `webhook_id` from Shopify's registration).

### Proof of Concept
1. Attacker creates/uses a Shopify development or trial store (`attacker-shop.myshopify.com`) and installs the target app.
2. Attacker triggers any registered webhook topic (e.g., `orders/create`) on `attacker-shop.myshopify.com`; Shopify POSTs to the app's public webhook endpoint with headers:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   ```
3. Attacker captures `raw_body` and `X-Shopify-Hmac-Sha256` (their own server received them directly).
4. Attacker resends the identical request to the same endpoint, changing only:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
5. `ShopifyAPI::Webhooks::Request.new` parses this successfully (`lib/shopify_api/webhooks/request.rb:45-63`); `Utils::HmacValidator.validate` returns `true` because it only recomputes the HMAC over `@raw_body`, which is unchanged (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
6. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's event body>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled webhook data as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** docs/usage/webhooks.md (L20-30)
```markdown
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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
