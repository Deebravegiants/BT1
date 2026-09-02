The core issue mirrors the report's "check the identity, not each field" bug class: `ShopifyAPI::Webhooks::Registry.process` treats the HMAC-authenticated bytes and the tenant-identifying `shop` value as if they were the same authenticated unit, when in fact only the raw body is covered by the signature.

### Title
Webhook `shop` domain is not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` used for webhook dispatch from an HTTP header (`x-shopify-shop-domain`/`shopify-shop-domain`), but `ShopifyAPI::Utils::HmacValidator` only validates the raw request body against the app's `client_secret`-derived HMAC. The header carrying the tenant identity is never part of the signed material, so any caller who possesses one valid `(raw_body, hmac)` pair for the shared app secret can freely relabel which shop that payload is attributed to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an attacker-controlled header, entirely outside the signed payload: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` compute and compare the signature only over `verifiable_query.to_signable_string` (i.e., the body), never over the shop header: [3](#0-2) 

`Registry.process` accepts the request purely on the strength of this body-only HMAC check, then dispatches the handler using `request.shop`, which came from the unauthenticated header: [4](#0-3) 

The documented contract explicitly tells integrators that `data.shop` is "The shop domain of the webhook" and shows it being used directly to scope work per-tenant (e.g., `shop_domain: data.shop`): [5](#0-4) 

The broken identity binding, stated as an equality that the gem fails to enforce:
`shop value the HMAC actually authenticates (none — HMAC covers body only)` ≠ `shop value the handler/host app trusts for tenant scoping (header-derived request.shop)`.

Because the app's `client_secret` (and therefore the webhook HMAC key) is the same across every shop that installs the app, any shop that has the app installed can receive a legitimately-signed `(raw_body, hmac)` pair for its own events. Nothing in `Request` or `HmacValidator` binds that signed body to the specific shop domain claimed in the headers. An attacker (an ordinary merchant who installed the app on their own store) can:
1. Trigger a webhook event on their own store (e.g., `orders/create`) and capture the resulting `raw_body` and `x-shopify-hmac-sha256` value sent to their callback URL.
2. Replay that exact `raw_body`/HMAC to the app's webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to the victim shop's domain.
3. `HmacValidator.validate` passes (the body/HMAC pair is genuinely valid), and `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the victim's domain while the body content is the attacker's own data.

Depending on how the host application uses `data.shop` (as shown in the gem's own documented example, using it to key per-tenant background jobs/storage), this lets an attacker inject or misattribute data into another tenant's record, i.e., cross-tenant confusion driven entirely by a header the gem never authenticates.

### Impact Explanation
This breaks tenant isolation between shops sharing the same app installation — a Critical-class issue (cross-tenant access) per the scope. The `shop` field is the sole identity used by host applications (as documented) to route webhook payloads to the correct tenant's queue/database record; forging it via an unauthenticated header lets one merchant's traffic corrupt or spoof another merchant's tenant-scoped processing.

### Likelihood Explanation
Likelihood is significant: no special privilege is needed beyond installing the app on one's own store (a normal, low-friction action), and no cryptographic secret needs to be recovered — the attacker reuses a legitimately-issued HMAC for their own data while freely rewriting the co-located `shop` header, since `to_signable_string` never covers it.

### Recommendation
Include the tenant-identifying header (`shop-domain`) — along with `topic` and `webhook_id` — in the material that is HMAC-verified, or otherwise cryptographically bind the shop domain to the signed payload, analogous to validating every signer's identity rather than trusting an out-of-band claim. At minimum, `HmacValidator`/`Request` should not allow the `shop` value used by `Registry.process` for dispatch to be sourced from data that falls outside the verified signature.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the target app installed.
# Step 1: capture a real webhook fired by Shopify for attacker's own shop.
raw_body = capture_from_real_webhook_body   # e.g. '{"id":1,"note":"pwned"}'
hmac     = capture_from_real_webhook_header  # x-shopify-hmac-sha256 value, valid for Context.api_secret_key

# Step 2: replay to the app's public webhook endpoint, spoofing the shop header.
headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => hmac,               # still valid, body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true  (body/HMAC pair genuinely matches api_secret_key)
# handler.handle receives data.shop == "victim-shop.myshopify.com" with attacker-supplied body
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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
```
