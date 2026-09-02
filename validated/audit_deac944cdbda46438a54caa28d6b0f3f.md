### Title
Webhook `shop`, `topic`, `api_version`, and `webhook_id` are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that the registry hands to the app's handler are read from unauthenticated HTTP headers. This is the exact bug class described in the report: a field that is *acted on* by downstream logic (there, `tokenGasPriceFactor`; here, the webhook `shop` identity) is not included in the data that is cryptographically bound by the signature check.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac` is computed from the `hmac-sha256`/`x-shopify-hmac-sha256` header: [2](#0-1) 

`Registry.process` validates only this body-derived HMAC, then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all read straight from headers that are excluded from the signed bytes — directly to the app's webhook handler: [3](#0-2) 

The identity binding that should hold is:
`HMAC_valid(raw_body, secret) == true` **and** `shop_header ∈ signed_bytes`.

In this implementation only the first half holds; `shop_header` (and `topic`/`webhook_id`/`api_version`) are never part of `signable_string`, so:
`HMAC_valid(raw_body, secret) == true` while `shop_header` is completely unauthenticated.

Because `OpenSSL::HMAC.hexdigest` is computed over `@raw_body` alone, any request with a given body and a valid signature for that body will pass `Utils::HmacValidator.validate` regardless of what `shop-domain` header accompanies it — exactly analogous to how `tokenGasPriceFactor` could be swapped after signing because it wasn't part of `encodeTransactionData`.

### Impact Explanation
A merchant who has installed the app on their own store (an "unprivileged internet user" with respect to any other tenant) legitimately receives Shopify-signed webhook deliveries for their own shop, with a valid `hmac-sha256` over the body. Because the signature never binds the `shop-domain` (nor `topic`/`webhook_id`) header, that attacker can replay the exact same signed body to the app's webhook endpoint while substituting a victim shop's `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. `Utils::HmacValidator.validate` still returns `true` (it only checks the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(shop: <victim shop>, topic: <attacker-chosen topic>, body: <attacker-controlled body>, ...)`. Any host application that uses `WebhookMetadata#shop` (as intended/documented by this gem) to select the tenant record, session, or access token to act on will have attacker-controlled data attributed to, and processed under, a different merchant's tenant — a cross-tenant confusion caused entirely by this gem's signature scope, not by host misuse of the API.

### Likelihood Explanation
Exploitation only requires the ability to install the app on any shop (i.e., become a legitimate merchant/tenant of the app) and to make an HTTP POST to the app's public webhook endpoint with edited headers — no access token, `api_secret_key`, or privileged access is required. The gem's own `Registry.process` performs no cross-check between the signed body and the header-derived `shop`/`topic`/`webhook_id`, so every consumer of this library inherits the weakness unless it independently re-verifies the shop out-of-band.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the data that is HMAC-verified, e.g., by having `Request#to_signable_string` incorporate the header values in addition to `@raw_body`, or by requiring/validating that the shop is embedded in and consistent with the signed body (as Shopify's admin GraphQL webhook payloads typically already carry shop context). Alternatively, `Registry.process` should independently validate that `request.shop` matches an expected/authorized shop before dispatching to handlers, rather than trusting the header value solely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) for their own store, capturing the genuine `raw_body` and its valid `x-shopify-hmac-sha256` header from Shopify.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body`/`hmac-sha256` but sets `x-shopify-shop-domain: victim-shop.myshopify.com`:
```ruby
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac,      # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request) # HmacValidator.validate passes; handler runs with shop: "victim-shop.myshopify.com"
``` [3](#0-2)  confirms `request.shop` (unverified) is passed straight into `WebhookMetadata` used by the handler, while [1](#0-0)  confirms the signature never covers that value.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
