This confirms the vulnerability: the gem's documented contract explicitly promises that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the `shop` field of `WebhookMetadata` handed to the app's handler is documented as "The shop domain of the webhook" [2](#0-1) , implying it is trustworthy tenant-identity data. In reality, `Registry.process` only validates `Utils::HmacValidator.validate(request)`, whose `to_signable_string` for `Webhooks::Request` returns solely `@raw_body` [3](#0-2) , while the `shop` used to populate `WebhookMetadata.shop` is read directly and unauthenticated from the `x-shopify-shop-domain`/`shopify-shop-domain` header [4](#0-3) . `Registry.process` forwards that unverified header value straight into the handler as the tenant identifier without any cross-check against the signed payload [5](#0-4) .

### Title
Webhook tenant identity (`shop` field) is not covered by HMAC validation, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to verify "the request did indeed come from Shopify" before invoking the app's webhook handler. In practice it only validates the HMAC over the raw request body. The `shop` value that is passed to the handler as the authoritative tenant identifier is taken from an HTTP header that is completely excluded from the signed content, so it can be freely substituted by anyone able to replay a validly-signed webhook body.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

`Registry.process` validates only this body-derived HMAC:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [5](#0-4) 

But `request.shop` is read straight from the `shop-domain` header, never included in `to_signable_string`:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [4](#0-3) 

Because a single Shopify app uses one shared `api_secret_key`/`client_secret` to sign webhooks for *every* shop that installs it [6](#0-5) , a valid `(raw_body, hmac)` pair generated for one tenant (e.g., an attacker's own store that installed the app) remains cryptographically valid when replayed with a different `x-shopify-shop-domain` header. The identity binding that should hold — "the shop whose HMAC signature is verified" equals "the shop attributed to the webhook payload" — is broken, since the header is never part of the signed bytes.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately controls one shop that has the vulnerable app installed can capture one of their own real, validly-signed webhook deliveries and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a victim merchant. `Registry.process` will accept it (HMAC over the body checks out) and dispatch `WebhookMetadata` with the attacker-chosen `shop` value to the app's handler, which per the gem's own documented usage pattern is expected to key persistence/business logic off `data.shop` (e.g., `perform_later(shop_domain: data.shop, ...)` in the documented example) [7](#0-6) . This can corrupt or inject data attributed to the wrong tenant — a cross-tenant confusion issue.

### Likelihood Explanation
Requires the attacker to have at least one installation of the app (a normal merchant relationship, not a privileged internal account) so they can obtain a genuinely signed webhook body/HMAC pair, plus the ability to POST arbitrary headers to the app's public webhook endpoint — both are available to an ordinary unprivileged user of the app ecosystem.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind the header-derived `shop` to the signed body before it is trusted and forwarded to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. for `orders/create`, with headers including `x-shopify-hmac-sha256: <valid-hmac>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`, and some raw JSON body `B`.
2. Attacker resends a POST to the app's webhook endpoint with the exact same raw body `B` and the exact same `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate(request)` recomputes HMAC over `@raw_body` (unchanged) and it matches, since `shop-domain` is never part of the signed content [3](#0-2) .
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))`, causing the app to process/store attacker-controlled order data as though it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L16-21)
```ruby
          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
```
