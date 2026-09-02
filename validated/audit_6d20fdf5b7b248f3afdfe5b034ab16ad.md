### Title
Webhook shop/topic attribution is not covered by the HMAC, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are used to route and attribute the webhook to a specific merchant — come from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` decodes the `hmac-sha256`/`x-shopify-hmac-sha256` header for comparison: [1](#0-0) 

`HmacValidator.validate` (via `Utils::HmacValidator`) authenticates exactly this signable string against `Context.api_secret_key`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as authorization to trust the request, and then forwards `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the signed bytes — straight to the app's handler as the tenant identity for the event: [3](#0-2) 

Because the app's `api_secret_key` is a single shared secret across every shop that installs the app (not per-shop), any merchant who installs the app receives genuinely-signed webhooks for their own store. That merchant can capture a valid `(raw_body, hmac-sha256)` pair from their own store's webhook, then replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`) header to name a *different* victim shop. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop's `data.shop`, even though the shop header was never bound to the signature.

This is the same bug class as the underlying report: a field that downstream logic acts on (`shop`/`topic` attribution) is not covered by the integrity check (HMAC), so satisfying the check does not guarantee the identity is authentic.

### Impact Explanation
Any app built on this gem that keys per-tenant state (order/customer records, install status, session/token lookups, background job dispatch) off `WebhookMetadata#shop` as returned by this library is vulnerable to cross-tenant data injection: an attacker-controlled merchant can cause fabricated (but HMAC-"valid") webhook payloads to be attributed to a different shop's tenant, i.e., cross-tenant access/injection — a Critical-tier impact per the rules.

### Likelihood Explanation
The prerequisite is trivial: the attacker only needs to be able to install the target app on a shop they control (most Shopify apps can be freely installed on a development or trial store) and capture one real webhook from Shopify to their own endpoint. No access token, `client_secret`, or TLS interception is required — only crafting a new HTTP request with a captured, still-HMAC-valid body plus an arbitrary `shop-domain`/`topic` header value.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable material verified by the HMAC, or independently verify that the `shop` header corresponds to a shop with an existing, valid session/installation before trusting it in `WebhookMetadata`. At minimum, document prominently that `request.shop`/`request.topic` are not authenticated by `HmacValidator.validate` and must be cross-checked by the host application against known installed shops.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Capture a genuine webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
3. Replay a new POST to the app's webhook endpoint with the same body `B` and header `H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` because it only checks `B`/`H`; `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: parsed(B), ...)`, causing the app to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
