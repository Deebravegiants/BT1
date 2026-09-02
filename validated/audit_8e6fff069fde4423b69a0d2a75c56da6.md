Confirmed: the webhook `topic`, `shop-domain`, `webhook-id`, and `api-version` values are all taken from unauthenticated HTTP headers, while `HmacValidator.validate` (via `VerifiableQuery#to_signable_string`) only signs the raw request body.## Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, but that validation only covers the raw request body. The `shop` (tenant) identity that is actually acted upon by the app comes from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never included in the signed bytes. This breaks the identity binding: `shop authenticated by HMAC` ≠ `shop attributed to the processed webhook data`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the raw body only: [2](#0-1) 

`Registry.process` gates all further processing on that same check, then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id`, all of which are read straight from HTTP headers instead of from the signed payload: [3](#0-2) 

`request.shop`, `request.topic`, and `request.webhook_id` are simple header lookups with no cryptographic binding to the body or to each other: [4](#0-3) 

The gem's own documentation reinforces the false assumption that `process` "will verify the request did indeed come from Shopify" as a whole, when in fact only body integrity is verified: [5](#0-4) 

This is the same bug class as the analog report: a value that is *acted on* (there, "which proposal is being processed"; here, "which shop the webhook belongs to") is never checked against the value that was actually *authenticated* (there, the currently active proposal; here, the HMAC-signed bytes). Because the shop-domain header sits outside the signed data, any entity capable of receiving one genuine, signed webhook (e.g., by installing the app on their own store — an unprivileged action) can capture a valid `(body, hmac)` pair and replay it to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` value, causing the app to process attacker-controlled, Shopify-signed content under a different shop's identity.

### Impact Explanation
This allows cross-tenant data injection/confusion: an attacker who legitimately installs the app on their own shop can forge webhook deliveries attributed to any other merchant shop domain, since the HMAC only proves "this body was generated with the app's secret for *some* webhook," not "for *this* shop." Depending on the app's handler logic, this can be used to inject fake order/customer events into another tenant's data pipeline, or trigger mandatory compliance topics (e.g. `shop/redact`, `customers/redact`, `customers/data_request`) against a victim shop the attacker does not control, causing unauthorized data deletion or export actions scoped to the wrong tenant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged actor who can install the app on a shop they control receives real, correctly signed webhook deliveries and can capture the exact `(raw_body, hmac header)` pair. Replaying that pair to the app's webhook endpoint with a modified shop-domain header requires no secret material and no privileged access — only knowledge of the app's public webhook URL, which is attacker-controlled input per the documented integration pattern (`request.headers.to_h` passed directly into `Request.new`).

### Recommendation
Bind the shop identity to the authenticated request instead of trusting the header value used for routing:
- Include the shop domain (and ideally topic/webhook-id) in the signable string used for HMAC verification, or
- After the app receives an access token/session for a given shop, cross-check that `request.shop` matches an actively registered/known shop before dispatching to the handler, and reject mismatches, or
- At minimum, document and enforce in `Registry.process` that `request.shop` must be independently verified by the host application against a known session store keyed by shop, treating the header as untrusted routing metadata rather than an authenticated fact.

### Proof of Concept
1. Attacker installs the target app on their own Shopify development/trial store (`attacker-shop.myshopify.com`) — no special privilege required.
2. Shopify sends a legitimate webhook, e.g. `customers/data_request`, to the app's registered endpoint, with header `x-shopify-shop-domain: attacker-shop.myshopify.com`, a body `B`, and `x-shopify-hmac-sha256: H = HMAC-SHA256(secret, B)`.
3. Attacker captures `B` and `H` verbatim (they own the shop and control the recipient/proxy of the webhook).
4. Attacker POSTs to the app's public webhook endpoint with the exact same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, matches `H`, and returns `true` — [6](#0-5)  passes despite the shop header being forged.
6. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, so the app processes the attacker's replayed webhook as if it originated from the victim shop — [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
