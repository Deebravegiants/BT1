### Title
Webhook Shop-Tenant Spoofing via HMAC Not Covering the `shop`/`topic`/`webhook_id` Headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the shop-tenant identifier (`shop`), topic, and webhook id are read from HTTP headers that are never included in the HMAC-signed payload. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC against the body only and then dispatches the handler using the unauthenticated `shop` header. Anyone who can obtain one genuine, correctly-signed webhook delivery (e.g. by installing the public app on their own free/dev store) can replay that exact body+HMAC pair while substituting the `shopify-shop-domain` header of a victim store, and the library will treat it as an authentic webhook for the victim shop.

### Finding Description
The intended identity binding is: `shop that the HMAC certifies == shop that the handler acts on`. This binding is broken:

- `Request#hmac` and `Request#to_signable_string` are computed purely from the raw request body: [1](#0-0) 
- `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers, none of which participate in `to_signable_string`: [2](#0-1) 
- `Registry.process` only checks `Utils::HmacValidator.validate(request)`, i.e. `HMAC(secret, raw_body)`, and then immediately trusts `request.shop` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 
- `HmacValidator.validate` verifies exactly `verifiable_query.to_signable_string` (the raw body) against `verifiable_query.hmac` (the header-derived hmac) — it has no notion of `shop` at all: [4](#0-3) 

Because Shopify's webhook HMAC is computed by Shopify over the JSON body only (this is Shopify's own webhook signing scheme, which this gem faithfully mirrors), the `shop-domain`, `topic`, and `webhook-id` headers are *transport metadata*, not covered data. Any actor who is a genuine (even free-tier) merchant with the app installed receives real webhook deliveries for their own store with valid HMACs. That actor can capture one such body+HMAC pair and re-POST it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to an arbitrary victim shop domain (and, since `topic`/`webhook_id` are also unauthenticated, an arbitrary topic/id too). `HmacValidator.validate` still returns `true` because it only checks the body/HMAC pair, and `Registry.process` calls the registered handler with `shop: <attacker-chosen victim domain>` and the attacker's own body content.

The equality that should hold is:
`shop authenticated by HMAC == shop passed to WebhookMetadata/handler`
but in reality:
`shop authenticated by HMAC == "" (no shop is authenticated at all)` while `shop passed to handler == header value (attacker controlled)`.

### Impact Explanation
This is a cross-tenant confusion / spoofing primitive: an attacker (unprivileged relative to the victim tenant, only needing their own low-privilege install of the target app) can inject fabricated webhook events that host applications will process as if they originated from a different, victim shop. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` and `data.body` (e.g. to write orders, update inventory, trigger app-side entitlement/billing logic, or key a per-shop database record), this can lead to cross-tenant data corruption, unauthorized state changes attributed to a shop the attacker doesn't control, or forged/duplicated business events for a store the attacker has no access to — matching the "cross-tenant access" class of impact.

### Likelihood Explanation
Exploitation only requires: (1) installing the target public app on any store the attacker controls (trivial, e.g. a free Shopify dev/partner store) to obtain one legitimately signed webhook body+HMAC pair for a topic the app subscribes to, and (2) sending an HTTP POST to the app's webhook endpoint with that unmodified body/HMAC but an attacker-chosen `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header. No access to the app's `client_secret`, no victim credentials, and no privileged account are required — the whole point of the bug is that the HMAC's scope never includes the header fields the library treats as authoritative.

### Recommendation
Bind the tenant/topic identity into the signed payload check, e.g. have `Utils::HmacValidator.validate` (or a webhook-specific validator) require the `shop`, `topic`, and `webhook_id` to be supplied out-of-band from a source the app itself trusts (such as a lookup keyed by an already-authenticated session/shop, or by additionally verifying the shop domain against Shopify's known shop list before dispatch), rather than trusting the unauthenticated headers directly. At minimum, document prominently that `data.shop`, `data.topic`, and `data.webhook_id` in `WebhookMetadata` are **not** cryptographically bound to the HMAC and must not be used as an authorization boundary without additional verification (e.g. cross-checking against a session already on file for that shop).

### Proof of Concept
1. Install the target Shopify app (as any developer) on `attacker-shop.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: body `B` and header `x-shopify-hmac-sha256: H` where `H = Base64(HMAC-SHA256(client_secret, B))`.
2. Replay to the app's webhook endpoint:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H          # unchanged, still valid for body B
x-shopify-shop-domain: victim-shop.myshopify.com   # attacker-controlled
x-shopify-webhook-id: <any>
x-shopify-api-version: 2024-01

B
```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and compares to `H` — this succeeds because `B` and `H` are unmodified, confirmed by: [5](#0-4) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: B, ...)`, i.e. content the attacker fully controls is delivered to the app as if authenticated and originating from `victim-shop.myshopify.com`.

### Citations

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
