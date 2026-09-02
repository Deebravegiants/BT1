## Title
Webhook `shop-domain` and `topic` headers are trusted for tenant/topic dispatch but are not covered by the webhook HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers that are excluded from the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` then uses these unauthenticated header values to select the handler and to populate `WebhookMetadata`, which is the tenant-identifying data the host application relies on.

### Finding Description
`HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`. For webhook requests this is defined as just the raw JSON body: [1](#0-0) 

However, `shop`, `topic`, `api_version`, and `webhook_id` are parsed from headers that are never included in `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the body HMAC, then dispatches to a handler using the unauthenticated `topic` and passes the unauthenticated `shop` straight into `WebhookMetadata`, which apps use to scope tenant data: [3](#0-2) 

Because the app's `client_secret` is shared across every shop that installs the app, any shop that installs the app can legitimately receive genuine, correctly-HMAC'd webhook bodies for events it triggers itself (e.g. creating a product with attacker-chosen content). An attacker who controls such a shop can capture a valid `(body, hmac)` pair from their own genuine webhook delivery, then replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header to name a victim shop. `HmacValidator.validate` still succeeds because it only checks the body bytes, so the handler executes believing the (attacker-controlled) body belongs to the victim shop.

This is exactly the bug class from the report: a value that is acted upon (`shop`, used as the tenant key for storing/handling webhook data) is not covered by the integrity check (`hmac`, which signs only `body`). The binding that should hold — `hmac == HMAC(body ‖ shop ‖ topic)` — instead only holds as `hmac == HMAC(body)`, letting `shop`/`topic` be forged independently of the signed payload.

### Impact Explanation
This allows cross-tenant data injection/confusion: an unprivileged internet user who can install the app on their own shop (a normal, unprivileged action) can forge webhook deliveries that the host application will process as if they originated from a different, victim shop, without ever needing the app's `client_secret` or a victim access token. This satisfies the "cross-tenant access" Critical impact class, since data attributed to one merchant can be forged as belonging to another merchant's tenant record.

### Likelihood Explanation
Likelihood is meaningfully constrained: the attacker must (a) be able to install the target app on a shop they control to obtain a genuine `(body, hmac)` pair, and (b) be able to send arbitrary HTTP requests to the app's public webhook endpoint with custom headers — both are within reach of an unprivileged internet user and require no leaked secrets. The main limiting factor is that the forged webhook body content is restricted to whatever the attacker's own shop's events can produce (e.g., product/order fields), but many webhook topics carry attacker-influenceable body content (e.g. `products/create`, `orders/create`) which is enough to inject falsified data attributed to a victim shop.

### Recommendation
Include the identity-critical fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signed material, or otherwise cryptographically bind them to the body before dispatch — e.g., verify that the `shop` and `topic` headers match values embedded/expected within the validated request context, rather than trusting header values that sit outside the HMAC boundary. At minimum, document prominently that `shop`/`topic` headers are not authenticated by `HmacValidator.validate` so host apps do not rely on them for tenant isolation without additional verification (e.g., checking that the shop is one that is actually installed/known to the app before trusting body content for that shop).

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` (a normal unprivileged action).
2. Attacker triggers an event whose webhook body content they control, e.g. creates a product with a crafted title, causing Shopify to deliver a genuine `products/create` webhook to the app with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's real `client_secret`.
3. Attacker captures this `(raw_body, hmac)` pair (e.g., via a proxy they control since it's their own webhook endpoint traffic).
4. Attacker crafts a new POST request to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it validates against `request.to_signable_string` = `raw_body` only: [4](#0-3) 
6. The registered handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and attacker-controlled `body`, causing the host application to store/process attacker data under the victim shop's tenant.

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
