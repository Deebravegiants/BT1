Found in `webhooks/request.rb`: the `shop` used by the app (returned from `Request#shop`, line 21-23) is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, but the HMAC signature verified by `HmacValidator.validate` (via `to_signable_string`, line 36-38) only covers `@raw_body` — the shop-domain header is **not** part of the signed bytes at all.

### Title
Webhook `shop` identity is taken from an unauthenticated header not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with `to_signable_string` returning only the raw request body [1](#0-0) , while `shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates the HMAC over the body and, if valid, trusts `request.shop` to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `bytes verified by HMAC == bytes the app trusts as the tenant identifier`. Here that equality breaks: `HmacValidator.validate` computes `HMAC(secret, raw_body)` and compares it to the `hmac-sha256` header [4](#0-3) , but the `shop` value handed to the handler comes from a completely separate, unsigned header (`shop-domain`). Since the body is the only thing the signature binds, an attacker who can produce any body/HMAC pair that is valid for the app's secret (e.g., replaying a legitimately-captured webhook delivery for shop A, which they can observe on a network path they control, or via a malicious proxy/CDN in front of the endpoint) can resubmit that exact same signed body while substituting an arbitrary `x-shopify-shop-domain` header value for shop B. `Registry.process` will accept it because the HMAC check only validates the body content, not which shop the payload is claimed to originate from [5](#0-4) . The handler then executes business logic keyed on `request.shop`, i.e., under shop B's tenant identity, using data that was never bound to shop B.

### Impact Explanation
This lets an unprivileged attacker who can intercept or replay a single valid webhook delivery cross the tenant boundary: the payload's HMAC only proves "this body was sent by Shopify to *some* shop," not "this body belongs to *this* shop." Any host application that keys session/data lookups by `WebhookMetadata#shop` (as intended by this gem's API) can be made to apply attacker-chosen shop-A data/events under a different shop's identity — a cross-tenant data-integrity issue satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to already possess one valid `(raw_body, hmac)` pair for the app's secret (e.g. via a captured/replayed delivery, non-TLS relay, or logging leak on the wire before this gem's endpoint) — this gem's HMAC check itself cannot detect the substituted header because it was never designed to bind the domain header. Given webhook shop-domain headers are otherwise treated as trusted-and-verified by API consumers of this gem (the analog of `hmac_validator.rb`'s guarantees), the mismatch is a structural design gap rather than a one-off bug.

### Recommendation
Include the shop domain (and ideally topic/api-version) in the signable string, or independently verify that `shop-domain` matches a shop known to have valid delivery for the given signed body, before exposing `request.shop` to handlers.

### Proof of Concept
```ruby
# Attacker has captured one legitimate webhook delivery for shop-a.myshopify.com:
raw_body = '{"id":123}'
valid_hmac = "<hmac captured from Shopify's original delivery to shop-a>"

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,   # still valid: HMAC only signs raw_body
  "x-shopify-shop-domain" => "shop-b.myshopify.com",  # attacker-substituted
  "x-shopify-api-version" => "2024-01",
  "x-shopify-webhook-id" => "whatever",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) passes because it only hashes raw_body,
# and the handler receives WebhookMetadata(shop: "shop-b.myshopify.com", body: <shop-a's data>)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
