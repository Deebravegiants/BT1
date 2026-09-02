### Title
Webhook request HMAC does not cover the `shop`, `topic`, or `webhook-id` headers used to attribute and dispatch webhook data - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the tenant-identifying `shop-domain` header (and `topic`/`webhook-id`) are read unauthenticated and passed straight into the dispatched `WebhookMetadata`. Any actor who can produce one valid `(body, hmac)` pair signed with the app's shared `client_secret` — trivially available to any merchant who has installed the app, since that merchant's own legitimate webhook deliveries are signed with the same app-wide secret — can replay that pair to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still pass because it never inspects headers, so the webhook handler executes believing the payload belongs to a victim shop chosen by the attacker.

### Finding Description
`Webhooks::Request#to_signable_string` only returns the raw body: [1](#0-0) 

`hmac`, `shop`, `topic`, and `webhook_id` are all pulled directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC using only the signable string above, then dispatches to the handler using `request.shop` and `request.topic`, which were never part of what was verified: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm this: they only ever compare `verifiable_query.hmac` against a signature computed from `to_signable_string`, i.e. the body, never the headers: [4](#0-3) 

The equality that should hold but does not: `bytes verified by HMAC` == `bytes acted upon for tenant attribution`. Here, `bytes verified` = `raw_body` only, while `bytes acted upon` = `raw_body + shop-domain header + topic header + webhook-id header`. Because the `client_secret` used to sign webhooks is the same for every shop that has installed a given app (it is the app's secret, not a per-install secret), any merchant that has the app installed can legitimately trigger a webhook delivery to themselves, capture the `(body, hmac)` pair Shopify computed for their own store, and replay that exact pair against the app's own webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header for a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
If the host application's webhook handler uses `data.shop` (as documented/intended, see `WebhookMetadata.new(topic:, shop:, body:, ...)` in `registry.rb`) to decide which merchant's records to create/update/delete, an attacker who is merely one merchant among many app installs can inject a payload of their choosing that is attributed to any other shop known to have installed the app. This breaks the tenant boundary the HMAC is meant to enforce and constitutes cross-tenant access/injection — data intended to be scoped per-shop can be forged for an arbitrary victim shop using only a valid signature the attacker legitimately obtained for their own store.

### Likelihood Explanation
Medium. The attacker must (a) be, or control, at least one merchant that has the target app installed (very low bar — free, self-serve for most apps), (b) know or guess a victim shop's `myshopify.com` domain (often discoverable/enumerable), and (c) be able to POST directly to the app's public webhook endpoint (which is inherently internet-reachable, since Shopify itself must be able to deliver to it). No possession of `api_secret_key` or a stolen access token is required — the attacker only needs a webhook body+HMAC pair they legitimately received for their own store.

### Recommendation
Include the tenant-identifying and routing-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC validation, or otherwise cryptographically bind them to the body (e.g., compute the signature over `headers + body`, or require the caller to separately verify the shop is one it expects for that specific HMAC-covered payload) before constructing `WebhookMetadata` and invoking handlers.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook (e.g., `products/update`) to receive a legitimately Shopify-signed delivery: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Replay an HTTP POST to the app's webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally alter `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over the body and succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body` fully controlled by the attacker, even though Shopify never sent this payload for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
