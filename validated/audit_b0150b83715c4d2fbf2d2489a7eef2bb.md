## Answer

I found a valid analog: the webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body.

### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `Registry.process` only proves the integrity of the body — not of the `shopify-shop-domain` header that the library uses to identify which merchant/tenant the webhook belongs to.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
so `to_signable_string` is exactly the raw body, excluding `topic`, `api_version`, `webhook_id`, and critically `shop` (read from the `shopify-shop-domain`/`x-shopify-shop-domain` header): [2](#0-1) 

`Registry.process` validates only this HMAC-over-body, then immediately trusts `request.shop` as the tenant identity passed to the app's handler: [3](#0-2) 

The binding that should hold is: `HMAC-covered bytes == bytes that determine tenant identity`. Here it is broken: `HMAC(raw_body) ✓` but `shop-domain header ∉ HMAC(raw_body)`. Any request with a given body and its correctly-computed HMAC (e.g. a genuine webhook delivery captured from Shop A, where the attacker is a legitimate merchant/installer of the app) can be replayed with the `shopify-shop-domain` header rewritten to Shop B. `Registry.process` will pass HMAC validation (because the body/HMAC pair is untouched) and hand the handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` while the body content actually belongs to Shop A.

### Impact Explanation
This is a cross-tenant identity confusion: a host application that uses `WebhookMetadata#shop` (as documented/intended, see `webhook_handler.rb`) to select which merchant's session/records to update will attribute Shop A's body data to Shop B, or vice versa — enabling cross-tenant data injection into a victim shop's local state without needing that shop's credentials. This satisfies the Critical "cross-tenant access" criterion since the tenant boundary (`shop`) is not covered by the authentication primitive the gem itself provides and documents as trustworthy.

### Likelihood Explanation
Exploitability requires the attacker to be able to obtain at least one legitimately HMAC-signed webhook body/signature pair for any shop that has installed the app (any unprivileged merchant/tester can trigger their own app webhooks and capture the raw POST), then resend it to the app's webhook endpoint with an altered `shopify-shop-domain` header. No `api_secret_key`, access token, or privileged account is needed beyond the attacker's own trivial installation — this is a plausible "unprivileged internet user" abuse case, but it does depend on the host application actually keying tenant selection off `WebhookMetadata#shop` (which is exactly the field the gem exposes for that purpose), so likelihood is Medium-High rather than certain in all integrations.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the signable string, or otherwise cryptographically bind the `shopify-shop-domain` header to the signed payload before `Registry.process` treats it as the tenant identity for the handler. At minimum, document that consumers must cross-check `WebhookMetadata#shop` against the shop associated with the session/store they expect, since the gem's own signature does not vouch for it.

### Proof of Concept
```ruby
# Attacker owns Shop A (attacker.myshopify.com) with a legit app install.
# They trigger any webhook and capture the real POST from Shopify:
raw_body = '{"id": 1, "note": "hello"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
real_hmac_b64 = Base64.strict_encode64(real_hmac) # valid signature Shopify computed for Shop A's delivery

# Attacker replays the same body+hmac to the app endpoint, but swaps the shop header:
headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => real_hmac_b64,       # still valid, since HMAC only covers raw_body
  "shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (validates raw_body only)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...))
# The app now believes this order data belongs to victim-shop, not attacker's own shop.
``` [4](#0-3)

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
