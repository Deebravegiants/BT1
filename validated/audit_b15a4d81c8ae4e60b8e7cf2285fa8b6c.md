Based on my review of the webhook verification code, I found a concrete identity-binding break that matches the requested bug class ("a field acted on but not covered by the HMAC").

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are trusted for tenant attribution without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never mixed into the signed material. `Registry.process` accepts any request whose body-only HMAC checks out and then hands the header-derived `shop` value to the webhook handler as the tenant identifier, breaking the equality `shop authenticated by HMAC == shop used to attribute the event`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled from HTTP headers, not from the signed payload: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e. the body) against the HMAC: [3](#0-2) 

`Registry.process` treats a body-only HMAC pass as authorization to trust `request.shop` as the tenant for the event and dispatches it to the handler: [4](#0-3) 

Because the `shop-domain` (and `topic`/`webhook-id`/`api-version`) header is never part of the signed string, an attacker who obtains one valid `(raw_body, hmac)` pair (e.g. from a webhook delivered to a shop they control/install the app on, or via any interface that surfaces the delivery details) can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The HMAC check still succeeds because it only verifies the body bytes, but the handler receives `WebhookMetadata` attributed to the attacker-chosen shop: [5](#0-4) 

This is the exact identity-binding gap called out in the review rules: "a field acted on but not covered by the HMAC." The gem verifies "this body came from someone who knows the client secret," but the handler acts as if it also verified "and this body belongs to shop X" — the two claims are not bound together.

### Impact Explanation
Any app whose webhook handler uses `WebhookMetadata#shop` to select which tenant's data/config/access token to act on (a standard and encouraged pattern for multi-tenant Shopify apps) can be made to process attacker-supplied event data under a victim shop's identity. Depending on the topic (e.g. `app/uninstalled`, `customers/redact`, `shop/redact`, order/product topics that trigger tenant-scoped side effects), this enables cross-tenant data corruption, spoofed compliance/redaction actions against a shop that never issued them, or misattributed business events — a cross-tenant integrity/data-attribution breach.

### Likelihood Explanation
Exploitation requires the attacker to obtain one legitimately-signed `(body, hmac)` pair, which they can generate themselves by installing the app on any shop they control and having Shopify deliver a webhook (topic/body content can often be influenced by the attacker's own shop actions, e.g. naming fields, since the HMAC only binds the body, not the shop). No access to `client_secret`, access tokens, or privileged accounts is needed — only the ability to receive one authentic webhook and replay it with a modified header, which any unprivileged internet user capable of installing/using the app on a store can do.

### Recommendation
Bind the identity fields into the signed material or otherwise re-verify them out of band: either include `shop`, `topic`, and `webhook_id` in the HMAC-covered string (mirroring how `AuthQuery#to_signable_string` binds `shop`/`host`/`state` into its signature), or have `Registry.process`/consuming apps cross-check `request.shop` against an independently trusted source (e.g. the session/shop the webhook subscription was registered for) before trusting it for tenant-scoped actions.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives (or otherwise obtains) one legitimate webhook delivery:
raw_body = '{"id": 1, "note": "hello"}'
valid_hmac_b64 = "<hmac Shopify computed with the app's client_secret over raw_body>"

# 2. Attacker replays the exact same body+hmac to the app's public webhook
#    endpoint, but swaps the shop header to a victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,       # unchanged, body unchanged -> still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) passes because it only checks raw_body against the HMAC.
# The handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed_body, ...)
# and performs tenant-scoped logic for "victim-shop" using attacker-supplied body content.
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
