I've confirmed the vulnerability path. In `ShopifyAPI::Webhooks::Registry.process`, the HMAC signature only covers the raw request body (`to_signable_string` returns `@raw_body` in `lib/shopify_api/webhooks/request.rb`), while the `shop` value that the handler receives and acts on is read directly from the `X-Shopify-Shop-Domain` header — a header that is never included in the signed content. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop identity not bound to HMAC signature allows cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the raw request body only, then trusts the `shop` value taken from the unauthenticated `X-Shopify-Shop-Domain` header when invoking the app's webhook handler. Because the shop identifier is not part of the signed content, a party that has ever received one legitimate webhook (e.g. for their own store) can capture that body/HMAC pair and replay it against the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header, causing the handler to process data under a victim tenant's identity.

### Finding Description
The equality this gem should enforce is: `shop value the handler acts on == shop value cryptographically bound to the signed payload`. Instead, `HmacValidator.validate(request)` recomputes an HMAC over `request.to_signable_string`, which is defined as `@raw_body` only [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read straight from HTTP headers via `shopify_header`, none of which are covered by the signature [4](#0-3) .

`Registry.process` performs the HMAC check and, once it passes, unconditionally builds `WebhookMetadata` using `request.shop` from the header and hands it to the app's handler: [3](#0-2) 

Since the same `Context.api_secret_key` is shared across all shops using the app (it is the app's secret, not a per-shop secret), any body that produces a valid HMAC for shop A's webhook can be resent with the header changed to shop B's domain, and the signature will still validate — the gem never checks that the header-provided `shop` matches anything cryptographically tied to the signature.

### Impact Explanation
This breaks the tenant-isolation guarantee webhook processing is supposed to provide: apps that key persistence/business logic off `data.shop` (as documented in `docs/usage/webhooks.md` and shown in the reference handler example) will process/store data under an attacker-chosen shop identifier. This is a cross-tenant access issue — an untrusted actor can cause data belonging to (or attributed to) one merchant to be attributed to a different merchant record purely by manipulating a header on a replayed, still-validly-signed request.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one valid `(raw_body, hmac)` pair, which is trivial if the attacker controls or has access to any shop that has the app installed (a normal, low-privilege capability for a public app), or if such a payload leaks/is logged. No access token, `client_secret`, or privileged account is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-controlled headers.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed material — e.g., derive `to_signable_string` from a canonical concatenation of `raw_body` and the shop header, or, more robustly, validate on the backend that the `X-Shopify-Shop-Domain` header matches a shop with an active, previously-registered session/subscription for that specific webhook id before dispatching to the handler. At minimum, document prominently that `request.shop` is unauthenticated and must be cross-checked against known-installed shops before use.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (attacker controls shop-a, or has observed one legitimate webhook).
2. Shopify sends a legitimate webhook to the app for `shop-a`: body `B`, `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
3. Attacker captures `(B, H)` and replays a POST to the app's webhook endpoint with the same body `B` and same header `H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `Registry.process` calls `HmacValidator.validate`, which recomputes HMAC over `B` only and succeeds (since `to_signable_string` never includes the shop header) — see `lib/shopify_api/webhooks/request.rb` lines 35-38 and `lib/shopify_api/webhooks/registry.rb` line 190.
5. `WebhookMetadata` is built with `shop: "shop-b.myshopify.com"` (from the header) and dispatched to the app's handler, which processes/persists the replayed payload as if it belonged to shop-b — line 198 of `registry.rb`.

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
