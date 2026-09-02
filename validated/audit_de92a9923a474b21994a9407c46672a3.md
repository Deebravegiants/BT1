## Title
Webhook shop-domain identity spoofing via cross-tenant HMAC replay — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the **raw body**, then trusts the `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is **not covered by the HMAC**. Because the signing secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, any merchant who has legitimately installed the app can capture one of their own genuine webhook deliveries and replay it against the app's webhook endpoint with the `shop-domain` header changed to a victim shop, producing a webhook that verifies successfully but is attributed to the wrong tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header, entirely outside the signable string: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature exclusively from `to_signable_string`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication, then forwards `request.shop` (the unauthenticated header) directly to the app's handler as the tenant identity: [4](#0-3) 

The broken binding, stated as an equality that fails to hold:
`shop authenticated by HMAC` ≠ `shop stored/used as the tenant key (request.shop / WebhookMetadata#shop)`

Since the HMAC secret (`api_secret_key`) is shared across all shops for a given app (it is the app's own `client_secret`, not a per-shop secret), any attacker who is themselves a legitimate merchant installing the app can:
1. Receive a genuine, correctly-signed webhook from Shopify for their own shop (`attacker-shop.myshopify.com`).
2. Take that exact `raw_body` and `HMAC` (both unchanged and still valid, since the HMAC never covered the shop header).
3. Replay the POST to the app's webhook endpoint, substituting `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` passes because it only checks the body signature.
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-controlled data as if it came from the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an app that keys any data, side effects, or authorization decisions in its webhook handler off `WebhookMetadata#shop` (the documented and expected way to identify which merchant a webhook is for) can be made to apply attacker-supplied webhook bodies to another merchant's tenant record. This matches the Critical "cross-tenant access" impact category, since it lets one authenticated tenant (any merchant who installed the app) inject events attributed to a different tenant.

### Likelihood Explanation
Requires only that the attacker be a legitimate, unprivileged installer of the target app (any merchant can install a public app) and have network access to the app's public webhook endpoint — no leaked credentials, TLS interception, or privileged account needed. Capturing one's own webhook payload/HMAC pair and replaying it with a modified header is trivial.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable content, or otherwise cryptographically bind the shop domain to the verified payload before trusting `request.shop`/`WebhookMetadata#shop`. At minimum, document prominently that `shop-domain` is unauthenticated and must not be used as a tenant lookup key without additional verification (e.g., cross-checking against a known/expected shop for that webhook subscription).

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and legitimately installed the app.
# They receive a real Shopify webhook:
raw_body = '{"id":123,"note":"hi"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Replay it, only changing the shop header to a victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac untouched)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

### Citations

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
