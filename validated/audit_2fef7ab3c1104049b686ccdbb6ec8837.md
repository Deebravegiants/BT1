### Title
Webhook shop-domain, topic, and webhook-id headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then hands the handler a `WebhookMetadata` object built from `request.shop`, `request.topic`, and `request.webhook_id` — none of which are included in the signed material. Any actor who can obtain one valid `(raw_body, hmac)` pair (e.g., by legitimately receiving a webhook for their own shop) can replay that exact body/HMAC to the app's shared webhook endpoint while forging the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header to name a different, victim shop. The gem will accept it as authentic and hand the handler data attributing the (attacker-controlled) body to the victim's tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all parsed straight from unauthenticated HTTP headers: [2](#0-1) 

`HmacValidator.validate` verifies `computed_signature = HMAC(secret, request.to_signable_string)` against the received `hmac`, i.e. it only proves the *body* bytes were signed by Shopify with the app secret — it says nothing about which shop, topic, or webhook id those bytes are attached to: [3](#0-2) 

`Registry.process` then trusts these unauthenticated fields directly, forwarding `request.shop` as the tenant identity to the app-supplied handler once the (body-only) HMAC check passes: [4](#0-3) 

This breaks the intended identity binding: `authenticated_shop == shop_the_handler_acts_on`. The HMAC only proves "this body came from Shopify for *some* webhook signed with our secret"; it does not prove "this body came from Shopify *for shop X*". Because the webhook endpoint is a single shared HTTP route for all shops (as shown in the gem's own docs), an attacker only needs to capture one legitimate `(raw_body, hmac)` pair delivered to them for their own shop, then re-POST it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop domain: [5](#0-4) 

This is particularly severe for the mandatory GDPR compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`), which are dispatched through the exact same `process` path and rely entirely on `data.shop` to know whose data to return or erase: [6](#0-5) 

An attacker who installs the app on their own shop (a normal, unprivileged onboarding step requiring no special credentials) can trigger a real `customers/data_request` or `orders/create` webhook containing attacker-chosen content, capture the resulting valid `(body, hmac)`, and replay it against the shared endpoint with the shop header set to a victim's domain. Any app whose handler trusts `data.shop` to select which tenant's session/data to act on (the documented, intended usage pattern shown in `docs/usage/webhooks.md`) will process/return/delete data under the wrong tenant, or attribute attacker-supplied order/customer content to the victim's shop.

### Impact Explanation
This crosses a tenant boundary using only the capabilities of a normal, unprivileged multi-tenant participant (installing the app on one's own shop) — no access token, `client_secret`, or leaked credential is required. The consequence is cross-tenant data confusion/exfiltration or spurious data injection attributed to a shop that never sent the request, matching the Critical "cross-tenant access" impact category. The root cause is structurally identical to the reported bug class: a field (`shop`, and likewise `topic`/`webhook_id`) is acted upon by the library/handler but is not covered by the authenticity check (HMAC), exactly as the H-1 report describes a value used for security-relevant accounting that is not covered by the validation it should be bound to.

### Likelihood Explanation
Any developer following the gem's own documented pattern (single shared webhook route, handler trusts `data.shop`) is exposed. The only precondition is that the attacker can receive at least one legitimate webhook (trivial — install the app on a shop they control, or trigger any topic they've subscribed to) and can send an arbitrary HTTP POST to the app's public webhook URL with custom headers, which is inherent to how HTTP webhook endpoints work.

### Recommendation
Bind the security-relevant headers into the signed material actually verified, or otherwise cryptographically/contextually bind `shop` to the caller before trusting it:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (this requires coordinating with Shopify's signing scheme, which currently only signs the body — so in practice this must be mitigated at the registry/handler level).
- At minimum, document and/or enforce in `Registry.process` that `request.shop` must be cross-checked against an expected/registered shop (e.g., looked up via the per-shop webhook subscription id) before being handed to handlers, rather than trusted as-is from an unauthenticated header.
- Provide per-shop distinct callback paths/tokens so a captured `(body, hmac)` pair cannot be replayed against a different tenant's context.

### Proof of Concept
```ruby
# Attacker installs the app on shop "attacker.myshopify.com" and receives a real
# webhook delivery for a topic they control, e.g. "customers/data_request":
raw_body = '{"customer": {"id": 1}, "orders_requested": [...]}'   # attacker-influenced content
hmac     = "<valid HMAC Shopify computed with the app's real client_secret over raw_body>"

# Attacker replays the exact same body + hmac to the app's shared webhook endpoint,
# but forges the shop-domain header to target a victim shop:
headers = {
  "x-shopify-topic"       => "customers/data_request",
  "x-shopify-hmac-sha256" => hmac,                       # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com" # forged
}

ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
)
# HmacValidator.validate only checks HMAC(secret, raw_body) == hmac -> passes,
# because `shop` is never part of the signed data (Request#to_signable_string).
# The handler receives WebhookMetadata with shop == "victim-shop.myshopify.com",
# and will act (e.g. compile/return/delete customer data) as if this legitimately
# came from the victim tenant.
```

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

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
