### Title
Webhook HMAC Signature Does Not Bind the `shop` Domain, Enabling Cross-Tenant Webhook Replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
The reported bug class is a broken identity binding caused by a security check validating the wrong operand (using `new_price` instead of `old_price` as the denominator, so the check answers with respect to the wrong quantity). The equivalent binding break in this gem is in webhook processing: the HMAC signature only covers the request **body**, while the tenant identity (`shop`) that the registered handler acts on is taken from an **unsigned HTTP header**. The check answers "is this body authentic" but the code acts as if it answered "is this (shop, body) pair authentic."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop` is read from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string` (the body only) against `verifiable_query.hmac`: [3](#0-2) 

`Webhooks::Registry.process` then dispatches to the app's handler using the **unverified** `request.shop` header alongside the verified body: [4](#0-3) 

The binding the library implicitly claims to enforce is:
`{shop the app attributes the webhook data to} == {shop for which Shopify actually generated this signed body}`

What is actually enforced is only:
`HMAC(body) == received_hmac`

Because the shop header is outside the signed bytes, any two values are decoupled: a valid `(body, hmac)` pair generated for shop A's webhook can be resent by anyone who can reach the app's public webhook endpoint with the `shop-domain` header swapped to shop B. The HMAC check still passes because it only validates the body bytes, never the header.

### Impact Explanation
This is a cross-tenant identity confusion at the point where merchant-facing business logic keys off `shop`. An attacker who owns/controls a shop (a normal, unprivileged Shopify merchant) can:
1. Install the target app on their own shop and receive a legitimately-signed webhook (`raw_body`, `hmac`) from Shopify.
2. Replay that exact HTTP request directly to the app's public webhook endpoint, only changing the `x-shopify-shop-domain` header to a victim shop's domain.
3. `HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` invokes the app's handler with `shop: <victim>` and `body: <attacker's own data>`.

Depending on how the host app's handler uses `shop` (e.g., to look up/update tenant records, sync inventory/orders, or trigger downstream actions), this allows an unprivileged user to inject attacker-controlled data into another tenant's context — a cross-tenant access/injection primitive purely through this gem's own webhook verification API.

### Likelihood Explanation
The webhook endpoint is, by design, a public, unauthenticated HTTP endpoint (that is the entire premise of the HMAC check), so any internet user can send it a request. The attacker only needs to be a real, self-service Shopify merchant able to install the app on their own store to obtain one valid `(body, hmac)` pair — no leaked secrets, no privileged account, and no interception of TLS is required.

### Recommendation
Include the tenant-identifying headers (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) in the signed material that `HmacValidator` verifies, or otherwise cryptographically bind the header values to the HMAC before `Registry.process` trusts `request.shop` for dispatch. Alternatively, document and enforce that `shop` must be independently re-validated (e.g., against the app's known-installed shops) before the handler acts on it, rather than trusting the header solely because the body passed HMAC validation.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop and captures a real webhook delivery:
raw_body = '{"id": 1, "note": "attacker-controlled payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# 2. Attacker replays the exact same body+hmac to the app's public webhook endpoint,
#    only swapping the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),   # still valid: only body is signed
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only checks raw_body)
# => handler.handle(shop: "victim-shop.myshopify.com", body: attacker's JSON, ...)
```
`Registry.process` never re-validates that `request.shop` corresponds to the shop for which the body/HMAC was actually generated by Shopify.

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
