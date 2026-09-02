This confirms the vulnerability: the gem's own documentation explicitly instructs developers to trust `data.shop` (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), but that field is never bound to the HMAC signature.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body [1](#0-0) . The `Request#to_signable_string` used for that HMAC only returns `@raw_body`, never the `shop-domain`, `topic`, or `webhook-id` headers [2](#0-1) . Yet `request.shop` (parsed straight from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) is passed directly into `WebhookMetadata` and handed to the app's handler as the identity of the tenant that generated the event [3](#0-2) [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header used to attribute the webhook == shop domain cryptographically covered by the HMAC`. That equality is broken here.

Shopify webhook signatures are generated per-app (using the app's shared `api_secret_key`/`client_secret`), not per-shop. Any merchant that has installed the app is a legitimate holder of validly-HMAC-signed webhook deliveries for their *own* shop. Because the signable string is only the JSON body [5](#0-4) , and `HmacValidator.validate` checks nothing more than `computed_signature == received_signature` over that body [6](#0-5) , a malicious/compromised merchant can:

1. Receive a genuine webhook for their own shop (valid body + valid HMAC, since the secret is shared across all shops of the app).
2. Replay that exact `raw_body`/HMAC pair to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header (or `shopify-shop-domain`) with a victim shop's domain.
3. `Utils::HmacValidator.validate(request)` still succeeds because the HMAC only covers the body, which is unchanged [7](#0-6) .
4. `Registry.process` forwards `request.shop` (now the victim's domain) straight to the handler as `WebhookMetadata#shop`, with no re-verification [8](#0-7) .

The gem's own documentation reinforces the unsafe pattern by showing `data.shop` used directly to key merchant-scoped work (`shop_domain: data.shop`) [9](#0-8) , meaning any host application that follows the documented usage inherits this cross-tenant spoofing surface directly through this gem's API.

### Impact Explanation
This lets an attacker (any merchant with the target app installed) forge fake webhook events attributed to a different shop with a cryptographically "valid" signature from the perspective of this library. Depending on how the host app keys work off `data.shop` (e.g., looking up that shop's stored session/access token to act on its behalf, or writing data associated with that shop), this can lead to cross-tenant access/data corruption — one of the qualifying "Critical" impacts (cross-tenant access) since the library provides no way to distinguish a spoofed shop header from a legitimate one.

### Likelihood Explanation
Requires only that the attacker (or someone) operates their own installation of the target app to obtain one genuine signed payload/HMAC pair, then send an HTTP POST with a modified shop-domain header to the app's public webhook endpoint — no access token, secret, or privileged account needed. This satisfies the "unprivileged internet user" and "no privileged credential" constraint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable data, or independently verify that `request.shop` corresponds to a shop with an active, legitimately-registered webhook subscription/session before trusting it in `WebhookMetadata`. At minimum, the gem should document and/or enforce that host apps must cross-check `data.shop` against a known/authorized shop list rather than trusting it implicitly as tenant identity.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# Shopify sends a legitimately-signed webhook for that shop:
raw_body = '{"id":1,"note":"hi"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_API_SECRET_KEY, raw_body)

# Attacker replays it to the same endpoint, forging the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # still valid! body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (see request.rb:35-38, hmac_validator.rb:26-31)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
```

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
