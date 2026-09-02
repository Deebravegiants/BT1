## Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) values are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values that are handed to the app's handler are read straight from HTTP headers that are never included in the signed material, so they can be freely altered without invalidating the signature.

### Finding Description
`Utils::HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string`, and for a webhook `Request` that method returns only the raw body: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `api_version`, and `webhook_id` are all parsed from headers and are entirely outside this signed string: [3](#0-2) 

`Registry.process` checks the HMAC and then immediately forwards `request.shop` (and the other header-derived values) to the app's handler with no additional binding check: [4](#0-3) 

The equality that should hold is: `shop-header == shop-bound-by-signature`. In reality the HMAC only proves `body == HMAC(body, client_secret)`; it says nothing about which shop the header claims to be. Since a single app's `client_secret` (and therefore its webhook signing secret) is shared across every merchant shop that installs the app, any merchant who installs the app can capture a webhook payload that Shopify legitimately signed for their own shop, and their genuine HMAC remains valid on the exact same raw body no matter what value is placed in the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header. Re-POSTing that same body/HMAC pair to the app's webhook endpoint with the shop header changed to a different (victim) merchant's domain passes `HmacValidator.validate` unchanged, because the header is never part of the signed content.

### Impact Explanation
This breaks the tenant isolation the HMAC check is meant to provide: a malicious but otherwise unprivileged installer of the app (no special credentials, no leaked secrets, no TLS interception) can inject webhook events that the app's handler will process as originating from an arbitrary other shop. Any app logic that uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a very common pattern, and the one this gem's own documentation recommends) can be manipulated into writing or acting on cross-tenant data. This meets the "cross-tenant access" Critical impact bucket in scope.

### Likelihood Explanation
Any developer or merchant that can install the app (an unprivileged internet user relative to other tenants) automatically receives genuinely-signed webhooks for their own shop and can trivially replay them with a modified `shop-domain` header using nothing more than a HTTP client — no secret material or elevated access is required beyond normal app installation, which is the standard threat model for a multi-tenant Shopify app.

### Recommendation
Bind the shop (and ideally topic/api-version/webhook-id) into the value that is authenticated, e.g. by including these header values in the signable string used for HMAC verification, or by additionally verifying that the shop header corresponds to a shop for which the app holds an active session/installation before invoking the handler, rather than trusting it purely on the strength of a body-only HMAC.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; Shopify delivers a webhook with body `B` and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: H` where `H = HMAC(app_client_secret, B)`.
2. Attacker replays an HTTP POST to the app's webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `B` and matches `H` — validation succeeds (see `lib/shopify_api/webhooks/registry.rb:190` and `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker-controlled webhook data attributed to a shop the attacker does not own.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
