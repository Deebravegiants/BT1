This confirms the vulnerability. The gem's own documentation explicitly instructs developers to trust `data.shop` as the tenant identifier (`docs/usage/webhooks.md:14,26`: "shop, String - The shop domain of the webhook" and the example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), while the HMAC verification in `HmacValidator.validate` only covers `Request#to_signable_string`, which returns solely `@raw_body` — never the shop-domain header.

### Title
Webhook `shop` field is not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that the HMAC of the raw request body matches a signature computed with the app's `api_secret_key`. The `shop` field that is handed to the host application's handler (and that the gem's own documentation instructs apps to use as the tenant/shop identifier) is read straight from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of the signed material at all. Anyone who can obtain one valid `(body, hmac)` pair — trivially achievable by any merchant who installs the app on their own store and receives a real webhook — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the shop header, and the gem will report it as validated and pass the attacker-chosen shop through to the handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop` is a completely separate accessor sourced from headers, uninvolved in the signable string:
```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it to the `hmac` header:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [3](#0-2) 

`Registry.process` performs exactly this check and then forwards the unauthenticated `request.shop` straight to the app-supplied handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

The binding that should hold — `shop field trusted by the app == shop field authenticated by the HMAC` — does not hold: `WebhookMetadata.shop` is populated from bytes the HMAC never covers. The gem's own guidance (`docs/usage/webhooks.md:14,26`) tells app authors to treat `data.shop` as the authoritative tenant identifier (e.g. `shop_domain: data.shop`), so this API design directly leads host applications into cross-tenant trust of an unauthenticated value.

An unprivileged attacker who is simply a merchant/developer with their own store and app installation can:
1. Trigger any real webhook to their own registered endpoint, capturing a legitimate `(raw_body, x-shopify-hmac-sha256)` pair signed with the target app's real `api_secret_key` (which they never need to know — Shopify signs it for them).
2. Replay that exact body and HMAC to the same app's webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to any victim shop domain.
3. `HmacValidator.validate` still returns `true` because the header is never part of `to_signable_string`.
4. The app's handler receives `WebhookMetadata.shop == "victim-shop.myshopify.com"` and, per the gem's own recommended usage, uses it to route/associate the (attacker-controlled) webhook body data to the victim tenant's records.

### Impact Explanation
This breaks the identity binding between "shop authenticated by the gem" and "shop the host app associates data with," enabling cross-tenant data injection/corruption: an attacker can cause an app to process attacker-controlled webhook payloads (order data, product data, GDPR/compliance topics, etc.) as if they originated from a victim's shop, without ever needing the victim's or even the app's secret key. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High likelihood: any user who can install the app on a store they control (a normal, unprivileged action available to any Shopify merchant/developer) can obtain a valid signed webhook body/HMAC pair and replay it with a forged shop header using only a basic HTTP client — no credentials belonging to the app or victim are required.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values in the HMAC-signed material that `to_signable_string` returns, or otherwise cryptographically bind the shop domain to the webhook signature before trusting it, so that `HmacValidator.validate` fails whenever the shop-domain header has been altered relative to the signed request. At minimum, update the documentation to explicitly warn that `data.shop` is not authenticated by the HMAC check and must be cross-validated by the host app against a known/installed shop list before being used as a tenant key.

### Proof of Concept
```ruby
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "shhh", host_name: "app.example.com",
  scope: "read_orders", is_embedded: false, api_version: "2024-01",
)

raw_body = '{"id":1,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Attacker legitimately obtained `raw_body` + `valid_hmac` from a webhook fired to
# their OWN store ("attacker-shop.myshopify.com"), then replays it with a forged shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Passes HMAC validation and calls the handler with data.shop == "victim-shop.myshopify.com"
```

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
