Based on my research, I found a concrete analog vulnerability matching the requested bug class — an identity-binding field that is *not* covered by the HMAC signature.

### Title
Webhook `shop-domain` identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the separate, unsigned `shop-domain` header to identify which merchant the webhook belongs to. Because the HMAC never covers the shop identity, any holder of a valid `(body, hmac)` pair for the app's secret can relabel that payload as belonging to an arbitrary victim shop.

### Finding Description
The webhook signature is validated as: [1](#0-0) 

`Request#hmac` and `Request#to_signable_string` show the HMAC is computed only over `@raw_body`: [2](#0-1) 

`Request#shop` reads the `shop-domain` header directly, completely independent of the signed content: [3](#0-2) 

`Registry.process` passes this unauthenticated `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identity: [4](#0-3) 

The equality that should hold is: **shop bound by HMAC == shop acted upon by the handler**. Here, the HMAC only proves `secret == HMAC_key(raw_body)`; it says nothing about which `shop-domain` the body is paired with. Any `(raw_body, hmac)` pair valid for the app's shared secret — obtainable by installing the app on an attacker-controlled/free development shop and capturing a genuine webhook delivery — remains valid HMAC-wise no matter what `shop-domain` header is sent alongside it, because the secret is shared across all shops using the same app credentials.

### Impact Explanation
An attacker who operates their own (even free/dev) shop with the target app installed receives legitimate webhook deliveries signed with the app's `api_secret_key`. They can replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Registry.process` will accept the request (HMAC validates against body, which is unchanged) and dispatch it to the app's handler with `shop: <victim-shop>`. If the host application uses this `shop` value to key data writes/lookups (a very common pattern this gem's documentation encourages, e.g., using `WebhookMetadata#shop` to look up sessions or update tenant records), the attacker achieves cross-tenant data confusion/injection — writing or triggering shop-scoped side effects attributed to a shop they don't own.

### Likelihood Explanation
Requires only: (1) installing the app on any shop the attacker controls (which any unprivileged internet user with a Shopify dev/partner account can do for free), (2) capturing one legitimate webhook delivery for a topic the app registers, and (3) resending it with a forged shop header. No access token, `client_secret`, or privileged account for the *victim* shop is needed — only ordinary access to install the app somewhere.

### Recommendation
Bind the shop identity into the authenticated content, e.g., include the `shop-domain` (and ideally `webhook-id`/`topic`) header values in the signable string used for HMAC validation, or independently verify that the shop in the header actually owns an active session/installation before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook POST, e.g. body `{"id":1}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-for-body>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Resend the identical body and HMAC header to the app's webhook endpoint, replacing only `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` (via `Registry.process`) succeeds because it only checks `raw_body` against the shared secret: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, despite the payload never having been sent by Shopify for that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
