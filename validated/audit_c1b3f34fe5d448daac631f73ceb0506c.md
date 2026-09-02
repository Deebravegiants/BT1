This confirms the shop attribution issue is documented as a trusted field passed directly from the webhook data to the app's handler.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` attribute — the tenant identifier passed to the app's webhook handler — is read from an unauthenticated HTTP header. This breaks the identity binding `HMAC(signed bytes) == HMAC(bytes actually trusted for tenant attribution)`, since the `shop-domain` header is never part of the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived entirely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed payload: [2](#0-1) 

`Registry.process` validates only the body HMAC via `Utils::HmacValidator.validate(request)`, then immediately builds `WebhookMetadata` using `request.shop` — the unauthenticated header — and dispatches it to the app's registered handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms the check is a pure comparison against `to_signable_string`, i.e., the raw body only, never the headers: [4](#0-3) 

The documentation confirms `data.shop` is treated by app authors as the authenticated tenant identifier for the webhook event, used directly for job dispatch/business logic: [5](#0-4) 

Because the HMAC only binds the body bytes, and Shopify signs webhooks with the single app-wide `api_secret_key` (the same secret for every shop that installs the app), any unprivileged internet user who has legitimately installed the app on their own store can:
1. Trigger a webhook with a predictable/fixed body (e.g., a compliance/mandatory topic such as `customers/redact`, or any webhook whose payload content can be made byte-identical across shops), capturing the resulting `hmac-sha256` header and body from their own legitimate delivery.
2. Replay that exact body + HMAC to the victim's webhook endpoint while substituting the `shopify-shop-domain` header with an arbitrary victim shop domain.
3. `HmacValidator.validate` succeeds (body and HMAC are unchanged and were legitimately signed by Shopify with the app secret), and `Registry.process` dispatches the event to the handler with `data.shop` set to the attacker-chosen victim domain.

This is exactly the identity-binding gap described in the report: a field acted upon (`shop`) is not covered by the HMAC that is used to authenticate the request.

### Impact Explanation
This crosses a tenant boundary: an app that trusts `data.shop` from the webhook handler (as the library's own documentation instructs) can be made to execute shop-scoped business logic — e.g., enqueueing background jobs, mutating per-shop state, or acting on compliance workflows like `customers/redact`/`shop/redact` — attributed to a victim shop the attacker does not control. This matches the "Critical - cross-tenant access" impact category, since it lets an attacker with only a legitimate but unprivileged installation of the app forge events on behalf of any other shop's tenant record.

### Likelihood Explanation
Exploitability depends on the attacker being able to produce a byte-identical (or attacker-influenced) webhook body that Shopify will sign, then replay it with a modified shop header directly against the app's public webhook endpoint. Mandatory compliance webhooks (`customers/redact`, `shop/redact`, `customers/data_request`) are good candidates since their bodies are often minimal/predictable and can be triggered by the attacker's own shop actions (e.g., uninstalling the app, requesting data erasure) at will. The endpoint is otherwise unauthenticated aside from this HMAC check, so likelihood is significant for any app relying on `data.shop` without independent verification.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed material, or otherwise cryptographically tie the header-derived shop to the signature — e.g., include the shop domain in the HMAC computation, or require the caller to independently verify that the shop belongs to a session/registration the app itself created (e.g., cross-check against the shop that registered for that specific topic/webhook id via the Registry). At minimum, update `HmacValidator`/`Request` so that `validate` fails unless the `shop-domain` header is authenticated as part of the signed payload, closing the gap between "bytes verified" (raw body) and "bytes trusted for tenant attribution" (headers).

### Proof of Concept
```ruby
# Step 1: Attacker installs the app on their own shop and lets Shopify deliver
# a mandatory webhook (e.g. customers/redact) with a minimal, predictable body.
raw_body = '{"shop_id":111,"shop_domain":"attacker-shop.myshopify.com"}' # example minimal body
# Attacker captures the legitimately-issued header:
# shopify-hmac-sha256: <valid HMAC of raw_body signed with the shared api_secret_key>

# Step 2: Attacker replays the exact same body + HMAC to the victim's endpoint,
# but swaps only the shop-domain header:
headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => captured_valid_hmac, # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (raw_body/HMAC pair is legitimate),
#    handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", ...)) is invoked,
#    causing the app to perform shop-scoped actions attributed to "victim-shop.myshopify.com"
#    even though the event was never actually sent for that shop.
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

**File:** docs/usage/webhooks.md (L12-27)
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
```
