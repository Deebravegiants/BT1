### Title
Webhook Shop/Topic Header Spoofing via HMAC That Only Covers Raw Body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are never included in the signed content. `Registry.process` validates the HMAC over the body only and then trusts these unsigned headers to build `WebhookMetadata`, so the shop identity delivered to the app's webhook handler is not cryptographically bound to the signature that authorizes the request.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic linkage to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the signed data: [3](#0-2) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop delivered to the handler`

But because the HMAC only signs the body, the equality actually enforced is:
`body authenticated by HMAC == body delivered to the handler`

with `shop`/`topic`/`webhook_id` completely outside the signed envelope. Anyone who can obtain one legitimate `(raw_body, hmac)` pair for any shop (e.g., a merchant who installs the app on their own store and captures the webhook their own store generates) can replay that same body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature check in `HmacValidator.validate` will still pass because it operates only on the body.

### Impact Explanation
If the host application trusts `WebhookMetadata#shop` to select which tenant's data to update (a common pattern — e.g., processing `app/uninstalled`, `shop/redact`, `customers/redact`, or inventory/order updates scoped by `shop`), an attacker can cause the webhook handler to execute shop-scoped side effects (data deletion, redaction, state changes) attributed to a victim shop of the attacker's choosing, without ever needing the app's `client_secret` or any privileged credential — this is a cross-tenant identity confusion (High impact per the rules).

### Likelihood Explanation
Exploitation requires only:
1. The attacker installs the app (or otherwise triggers) on any shop they control to receive one legitimate webhook delivery (a normal, unprivileged action available to any merchant).
2. Replay that exact body + HMAC to the app's public webhook endpoint with a forged `shop-domain` (and optionally `topic`/`webhook-id`) header.

No secret material, TLS interception, or privileged access is required, making this reachable by any unprivileged internet user who can install the target app once.

### Recommendation
Bind the shop/topic identity into the signed content that is verified, or otherwise cryptographically tie the header-derived `shop` to the request before it is handed to `WebhookMetadata`. Concretely:
- Extend `Request#to_signable_string` (or add a secondary check) to incorporate `shop`, `topic`, and `webhook_id` into what is verified, or
- Require host applications to independently confirm the `shop` header corresponds to a shop with a currently valid, stored access token/session before acting on the webhook, and document this requirement prominently since the gem's `Registry.process` currently does not enforce it.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and triggers any webhook (e.g. products/create), capturing:
raw_body = '{"id":123,"title":"x"}'   # body from the genuine webhook delivered to attacker's endpoint
hmac_b64 = "<value of X-Shopify-Hmac-Sha256 header from that genuine delivery>"

# 2. Attacker replays the exact same body/hmac to the app's public webhook
#    endpoint, but swaps the shop-domain header to target a victim shop:
headers = {
  "x-shopify-topic"        => "products/create",
  "x-shopify-hmac-sha256"  => hmac_b64,
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id"   => "attacker-controlled-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HMAC validation succeeds because it only checks raw_body, not the shop header:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the handler with the forged shop identity:
ShopifyAPI::Webhooks::Registry.process(request)
# handler receives WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
