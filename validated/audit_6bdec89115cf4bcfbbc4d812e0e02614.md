### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` (and `topic`/`webhook-id`/`api_version`) HTTP headers — which are never included in the signed payload — as the authenticated tenant identity handed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled straight from unauthenticated HTTP headers, with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — recomputes the HMAC over `to_signable_string` (i.e., the body only) and compares it to the `hmac-sha256` header: [3](#0-2) [4](#0-3) 

If the HMAC check passes, `Registry.process` immediately constructs `WebhookMetadata` using the unauthenticated `request.shop` value and dispatches it to the host app's handler as trusted data: [5](#0-4) 

The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook" — i.e., the documented contract is that `shop` is an authenticated field, when in fact only the body bytes are authenticated, not the shop identity.

**Identity binding broken (equality that should hold but doesn't):**
`hmac_covers(shop_header) == true` is assumed by callers, but in reality `hmac_covers(shop_header) == false`. The HMAC binds `secret ↔ raw_body`, not `secret ↔ (raw_body, shop)`.

Because a single app's `api_secret_key` is shared across every shop that installs the app, any actor who can install the (public) app on a shop they control can trivially obtain a batch of validly-signed `(raw_body, hmac)` pairs from real Shopify webhook deliveries to their own shop. They can then replay one of these bodies to the app's webhook endpoint while substituting the `shop-domain` header (and/or `topic`/`webhook-id`) with a victim shop's domain. The HMAC still validates (it never covered the header), so `Registry.process` calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, which the host application will treat as trusted data originating from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the whole `process`/HMAC mechanism exists to enforce: a webhook that is provably signed by the shared app secret can be attributed to an arbitrary shop chosen by the attacker, with attacker-controlled body content. Depending on how the host handler uses `data.shop`/`data.body` (updating per-shop records, triggering GDPR `customers/redact` / `shop/redact` mandatory-topic handling, syncing order/product state, etc.), this enables cross-tenant data corruption or injection attributed to a shop the attacker does not control — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) the ability to install the target (public) app on any shop the attacker controls — a normal, unprivileged action — to receive genuinely signed webhook deliveries, and (2) the ability to POST an HTTP request to the app's public webhook endpoint with a modified `shop-domain` header, which is exactly the shape of every legitimate webhook request. No access token, `client_secret`, or privileged account is needed — only observation of one's own legitimate webhook traffic.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the authenticated payload rather than trusting bare headers. At minimum, `Registry.process` should independently verify that the `shop-domain` header corresponds to a shop the application has actually installed/has an active session for before treating `data.shop` as authoritative, and/or the gem should require/encourage host apps to cross-check `request.shop` against their own installed-shop registry before acting on webhook data — document this gap explicitly since `to_signable_string` cannot be changed without breaking compatibility with Shopify's real signing scheme.

### Proof of Concept
1. Attacker creates/owns Shop A and installs the target public app on it; Shopify begins delivering real webhooks (e.g. `orders/create`) to the app's registered endpoint, each with a header set including `shopify-shop-domain: shop-a.myshopify.com`, `shopify-hmac-sha256: <valid HMAC over raw body>`, and a JSON body.
2. Attacker records one such `(raw_body, hmac)` pair — the HMAC is computed with `Utils::HmacValidator.compute_signature(raw_body, Context.api_secret_key)`, i.e., only over the body, per `hmac_validator.rb:33-40` and `webhooks/request.rb:35-38`.
3. Attacker crafts a new HTTP POST to the same webhook endpoint using the identical `raw_body` and `shopify-hmac-sha256` value, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this into a request object where `shop` returns `"victim-shop.myshopify.com"` while `hmac` still matches the (body-only) signature.
5. `ShopifyAPI::Webhooks::Registry.process(webhook_request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body, and then invokes the host's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's Shop-A body>, ...)` (`registry.rb:190-199`), which the host application processes as an authenticated event from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
