### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` attribute consumed by `ShopifyAPI::Webhooks::Registry.process` is read directly from the unauthenticated `x-shopify-shop-domain` HTTP header. Because the app-wide `client_secret`-derived HMAC never covers the shop-domain header, an attacker can take any body+HMAC pair that was legitimately signed for one shop and replay it against the app's webhook endpoint with a different `shop-domain` header, causing the handler to process the payload as belonging to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only the `@raw_body` is signed. The `shop` accessor, however, is derived purely from a header that plays no part in that signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. only the body bytes are checked: [3](#0-2) 

`Registry.process` raises if that body-only HMAC fails, but then trusts `request.shop` — sourced from the unauthenticated header — to build the `WebhookMetadata` object dispatched to the app's handler: [4](#0-3) 

The webhook HMAC secret is the app's own `client_secret` (`Context.api_secret_key`), shared across every shop that installs the app, not a per-shop value. Consequently, any entity that can install the app on their own store (an ordinary, unprivileged Shopify merchant) receives real, correctly-signed webhook deliveries for their own shop. Because the signature is computed only over the JSON body and never binds the `shop-domain` header, that same attacker can capture a legitimate `(raw_body, hmac)` pair from their own installation and resend it to the same app endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (the body/HMAC pair is genuine), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: <victim-domain>`, `body: <attacker-controlled-but-signed>` content. This breaks the identity binding `shop-authenticated == shop-that-produced-the-signed-bytes`, letting one tenant's traffic be attributed to another tenant purely by manipulating an unsigned header.

### Impact Explanation
This is a cross-tenant confusion vulnerability: a host application that keys any per-shop state (inventory sync, order processing, idempotency, webhook-driven billing, etc.) off `WebhookMetadata#shop` can be made to apply attacker-controlled (but validly-signed-for-a-different-shop) webhook payloads to a victim shop's record, without needing the victim's or the app's secrets. This matches the "cross-tenant access" Critical impact category, since it lets an unprivileged attacker (who is merely an installer of the same app) inject data attributed to another merchant's tenant.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's webhook processing path: the attacker only needs to install the target app on their own store (a normal, unprivileged action), capture one legitimate webhook delivery, and replay it with a modified header value — no access to the app's `client_secret`, no access token, and no interaction with the victim shop is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) to the HMAC-verified payload rather than trusting them as free-standing headers. For example, include the shop domain in the signable string (mirroring how it's included in the body of Admin GraphQL/Webhook payloads) or require callers to independently verify that the `shop-domain` header matches a shop record already known to have installed the app (e.g., cross-check against stored offline sessions) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g., `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify (a legitimate signature computed with the app's shared `client_secret`).
2. Attacker resends this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) and `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the secret: [5](#0-4) 
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)`, causing the host app to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-31)
```ruby
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
