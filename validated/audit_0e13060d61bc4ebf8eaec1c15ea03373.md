### Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC that covers the raw request body, then hands the caller-supplied `shop` header (unauthenticated) to the app's webhook handler as the tenant identity for that payload. Because the `shop` field is never part of the signed material, any bytes with a valid `(raw_body, hmac)` pair can be replayed with an attacker-chosen `shop` header, letting an unprivileged party attribute a genuine webhook payload to a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop` from the `x-shopify-shop-domain`/`shopify-shop-domain` header [1](#0-0)  but its `to_signable_string` (the value that gets HMAC-verified) returns only `@raw_body`, never the shop header [2](#0-1) .

`HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` and compares it to the supplied `hmac` [3](#0-2) . Since `to_signable_string` for a webhook `Request` is just the raw body, the `shop` value is completely outside the authenticated boundary.

`Registry.process` uses this same, body-only HMAC check as its sole authenticity gate, then forwards the unauthenticated `request.shop` directly into `WebhookMetadata`, which is delivered to the app's handler as the tenant identity for the payload: [4](#0-3) 

Because every shop that installs a given app shares the same `api_secret_key` (this is not a per-shop secret), an attacker can:
1. Install the target app on their own (attacker-controlled) development/test shop.
2. Trigger any webhook topic to observe a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
3. Replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain.

`Registry.process` will accept this as valid (the HMAC still matches, since it only covers the body) and dispatch it to the handler with `shop` equal to the victim's domain — an equality the gem never actually checked: `hmac-covered bytes == raw_body` while the tenant-binding claim `request.shop` is asserted with no cryptographic tie to those bytes at all. This breaks the identity binding `authenticated_shop == shop_used_for_tenant_action` that host applications rely on this gem to enforce, since the gem presents `request.shop` as the verified webhook's tenant.

### Impact Explanation
This is a cross-tenant confusion vector: a webhook payload cryptographically valid for shop A can be delivered to the app labeled as belonging to shop B. Mandatory topics such as `shop/redact`, `customers/redact`, and `customers/data_request` — explicitly recognized by this same registry [5](#0-4)  — as well as topics like `app/uninstalled`, are commonly used by host apps to key deletion/redaction/session-teardown logic off of `WebhookMetadata#shop`. An attacker can therefore trigger these actions against an arbitrary victim shop of their choosing, causing cross-tenant data manipulation without ever possessing the victim's credentials — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic for any attacker willing to install the target app on a free development store (a standard, unprivileged action for public/embedded Shopify apps), since that alone yields a validly-HMAC-signed payload they fully control the shop-domain header for. No secrets, tokens, or victim interaction are required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered material for webhook verification, or otherwise cryptographically bind `shop` to the signed payload before it is trusted as a tenant identifier in `Registry.process`/`WebhookMetadata`. At minimum, document that host applications must independently corroborate `shop` (e.g., against a shop that is actually known to have an active session/install) rather than trusting it purely because `HmacValidator.validate` returned true.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and captures a genuine webhook fired by Shopify to the app's endpoint, e.g.:
raw_body = '{"id":123,"note":"hi"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# 2. Attacker replays the exact body/hmac pair, but swaps the shop-domain header
#    to the victim's shop.
forged_headers = {
  "x-shopify-topic" => "shop/redact",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # unauthenticated
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. Registry.process succeeds because HmacValidator only checks raw_body,
#    and the handler is invoked with data.shop == "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(forged_request)
```
This demonstrates that `Registry.process` will accept and forward a webhook attributing arbitrary attacker-controlled `shop` values to any host application relying on `WebhookMetadata#shop` as an authenticated tenant identifier.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
