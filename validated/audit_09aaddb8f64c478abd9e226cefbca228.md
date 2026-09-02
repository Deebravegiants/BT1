Confirmed: there's no independent verification tying the `shop` field to the HMAC-signed content anywhere in `Registry.process` or `WebhookMetadata`. This confirms the identity-binding break.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header values are trusted as authenticated after HMAC verification, but only the raw body is covered by the HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as fully verified once `Utils::HmacValidator.validate` succeeds, and then forwards the request's `shop` header value to the app's handler as trusted, session-identifying data. However, the HMAC signature only ever covers the raw request body - the `shop-domain` header (and `topic`, `webhook-id`, `api-version`) are never part of the signed payload. Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is a single app-level secret shared across every merchant that has installed the app, any attacker who controls one shop's webhook feed (e.g. by installing the app on a free/dev store they own) can capture a validly-signed webhook body and hmac, then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to a victim shop domain. The `HmacValidator` check still passes because it only recomputes the HMAC over `@raw_body`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers with no cryptographic tie to the signed body:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Registry.process` performs a single gate - HMAC validity of the body - and then immediately treats the whole request (including `request.shop`) as an authenticated Shopify webhook:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

`HmacValidator.validate` computes the HMAC solely from `verifiable_query.to_signable_string` (i.e. the raw body) against `Context.api_secret_key`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [4](#0-3) 

The binding that should hold is: `shop header == the shop whose data actually produced this HMAC-signed body`. That equality is never checked. Because `Context.api_secret_key` is one value for the entire app (not scoped per shop), the same secret signs webhooks originating from *any* shop that installed the app. An attacker who owns a shop that has the app installed can:
1. Trigger a webhook topic they control (e.g. a `products/update`, or one of the mandatory topics like `customers/redact`) on their own store, capturing the raw body and the `X-Shopify-Hmac-Sha256` header Shopify computed for it.
2. Replay that exact body + hmac to the victim app's webhook endpoint, substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`, which are equally unauthenticated).
3. `HmacValidator.validate` still succeeds because the recomputed signature only depends on the untouched raw body.
4. `WebhookMetadata.shop` now reports `victim-shop.myshopify.com` to the app's handler, even though the payload and event never came from that shop.

This is the same root-cause class described in the reference report: a downstream consumer inherits a "proof" (a valid timer / a valid HMAC) that was only checked against a shared, non-identity-specific artifact, without validating a stronger claim that binds it to the specific origin/tenant identity it is later assumed to represent.

### Impact Explanation
Applications built on this gem use `WebhookMetadata#shop` as the trusted tenant key for mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`) and business events (`app/uninstalled`, `orders/create`, etc.) to route to per-shop data, sessions, and background jobs, per the gem's own documentation example (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). [5](#0-4)  A forged `shop` value lets an attacker who legitimately controls one installed shop cause the app to execute cross-tenant actions attributed to a victim shop - e.g. spoofing an `app/uninstalled` event to make the app revoke/delete the victim's stored session, or spoofing `customers/redact`/`shop/redact` to trigger deletion of a victim shop's data - without ever needing the victim's access token or credentials. This is a cross-tenant boundary crossing driven purely by unauthenticated header data, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own shop (trivially obtainable - any developer/partner can spin up a free development store) has the target app installed so they can receive genuinely-signed webhooks, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with attacker-controlled headers, which is inherent to any internet-reachable webhook receiver built with this gem's documented `Registry.process` pattern. No secrets, tokens, or victim cooperation are required, making this readily reachable by any unprivileged internet user who can install the target app once.

### Recommendation
Include the identity-bearing fields (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed payload the gem verifies, or otherwise cryptographically bind them to the raw body before trusting them. Where Shopify's own wire protocol constrains the signable payload to the body only, `ShopifyAPI::Webhooks::Request`/`Registry.process` should require and validate that `shop` corresponds to a shop with an active, previously-registered webhook subscription/session for the given `webhook_id`/topic before handing it to the handler as trusted metadata, rather than passing header-derived `shop` straight through as an authenticated value.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker-shop.myshopify.com`; trigger a mandatory webhook, e.g. `customers/redact`, and capture the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's single `client_secret`).
2. Replay to the victim app's webhook endpoint:
```
POST /webhooks/customers_redact
X-Shopify-Topic: customers/redact
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>

B
```
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) with `Context.api_secret_key`, matching `H` - validation passes.
4. `WebhookMetadata.new(shop: request.shop, ...)` yields `shop == "victim-shop.myshopify.com"`, and the registered handler executes shop-scoped logic (e.g., data deletion or session revocation) believing it is a genuine event for the victim shop, though the event and body actually originated from the attacker's own store.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
