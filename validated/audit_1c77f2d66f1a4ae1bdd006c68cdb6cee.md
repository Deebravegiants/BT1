### Title
Webhook shop-domain spoofing via HMAC that only covers the body, not the `shop` field - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` authenticate an incoming webhook solely via an HMAC computed over the raw request body. The `shop` value that is subsequently handed to the application's webhook handler is read straight from an HTTP header that is **not** part of the signed payload, breaking the binding `request.shop == shop that produced the HMAC`.

### Finding Description
`Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, and for webhooks that method returns just the raw body: [1](#0-0) 

The `shop` (and `topic`, `api_version`, `webhook_id`) accessor reads directly from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is completely outside the HMAC-signed data: [2](#0-1) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop` taken from that unauthenticated header, passing it straight to the app's handler: [3](#0-2) 

Because the `api_secret_key` used to compute/verify the HMAC is the same for every shop that has installed the app (it is the app's secret, not a per-shop secret), any party that can obtain one valid `(body, hmac)` pair for their own shop — for instance by installing the app on their own store and observing a legitimate webhook delivery — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed because the header is never part of the signed content, and `Registry.process` will happily report `data.shop` as the victim's domain to the handler.

### Impact Explanation
This breaks the identity binding: `request.shop` (the value acted upon by the host application to select which tenant's records to update) is not the value verified by the HMAC (only the body is verified). An attacker who has legitimately installed the app on their own shop (an unprivileged/low-trust position relative to other merchants) can spoof webhooks that appear to originate from a shop they do not control, causing the host application to process attacker-controlled webhook bodies (e.g. `orders/create`, `customers/redact`, `shop/redact`, app-specific topics) under another merchant's identity. This is a cross-tenant confusion/injection primitive stemming directly from this gem's verification logic.

### Likelihood Explanation
The prerequisite is only that the attacker has installed the app on any shop (a normal, unprivileged action any Shopify merchant can perform) and can capture one webhook delivery from their own store — no access token, `client_secret`, or `api_secret_key` value is ever needed, since the check only validates the body against the shared app secret, and the header is fully attacker-controlled in the replayed request.

### Recommendation
Include the `shop` (and other identifying fields such as `topic`, `api_version`) in the HMAC-signed payload verification, or otherwise cryptographically bind the header-derived `shop` value to the verified body before handing `WebhookMetadata` to handlers. At minimum, document/enforce that `data.shop` must never be trusted as a tenant-selection key without an additional, out-of-band confirmation (e.g., matching against a known set of shops that have this webhook registered), and consider mandatory HMAC coverage of headers akin to how `AuthQuery#to_signable_string` binds `shop` into its signed string. [4](#0-3) 

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw request body `B` and the resulting `x-shopify-hmac-sha256` header `H` (valid because `H = HMAC_SHA256(api_secret_key, B)` and `api_secret_key` is the same secret shared by the app across all installs).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, B) == H` — the spoofed `shop` header is never part of `to_signable_string`.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...))`, causing the host application's handler to act on `victim.myshopify.com`'s tenant using attacker-controlled body content.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
