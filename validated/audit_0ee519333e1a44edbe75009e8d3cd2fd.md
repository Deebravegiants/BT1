This confirms the vulnerability: the webhook HMAC only ever signs the raw body, never the `shop`, `topic`, `api_version`, or `webhook_id` values that come from HTTP headers, yet those header-derived values are handed to the integrator's `WebhookHandler#handle` as trusted, authenticated `WebhookMetadata`.

### Title
Webhook `shop` (and other metadata) header values are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `to_signable_string` method that the HMAC is computed over returns only `@raw_body` [2](#0-1) . However, the `shop`, `topic`, `api_version`, and `webhook_id` fields — all sourced from unauthenticated HTTP headers — are extracted separately from `@headers` and passed straight into `WebhookMetadata`, which the host application's `WebhookHandler#handle` treats as trusted, verified data [3](#0-2) [4](#0-3) .

### Finding Description
The binding that should hold is: `shop attributed to the webhook == shop whose data the HMAC-signed body actually belongs to`. Because `to_signable_string` only covers `@raw_body` [2](#0-1) , the `x-shopify-shop-domain` (or `shopify-shop-domain`) header is never part of the signed material verified by `HmacValidator.validate_signature` [5](#0-4) . Any request whose body+HMAC pair is valid (i.e., was genuinely computed by Shopify with the app's shared `api_secret_key` for *some* shop/topic) will pass validation regardless of what `shop-domain`, `topic`, `webhook-id`, or `api-version` headers are attached to it, since those headers are read independently in `Request#shop`, `#topic`, `#webhook_id`, `#api_version` [6](#0-5)  without cryptographic linkage to the body.

Since Shopify webhook HMACs are computed using the app-level `client_secret` (shared across every shop that installs the app) rather than a per-shop key, any merchant/tenant that installs the app receives legitimately-signed `(body, hmac)` pairs for their own shop. An attacker who controls one tenant can capture such a pair and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, and the signature will still validate because the header is outside the signed scope.

### Impact Explanation
This breaks the tenant-isolation boundary the HMAC check is meant to provide: `Registry.process` hands the handler a `WebhookMetadata.shop` value that the integrator's code will use to route/apply webhook data to a specific merchant/session, believing it was verified [4](#0-3) . A forged `shop` value lets a malicious tenant inject their own (validly-signed) webhook payload as if it originated from a different shop, i.e. cross-tenant data confusion/corruption in any host application that trusts `WebhookMetadata.shop` without independent verification (which the gem's own documentation and design encourages, since `shop` is presented as verified metadata alongside the HMAC check).

### Likelihood Explanation
Likelihood is moderate to high: exploitation requires only that the attacker be an installed/uninstalled tenant of the app (any unprivileged merchant, no elevated credentials) capable of triggering a webhook for their own shop and replaying the HTTP request to the app's public webhook endpoint with a modified `shop-domain` header. No knowledge of `api_secret_key` is needed because the attacker uses a legitimately Shopify-signed body from their own store.

### Recommendation
Include the `shop`, `topic`, `webhook_id`, and `api_version` header values in the HMAC signable string (or otherwise cryptographically bind them to the verified payload), or require the caller to independently authenticate the shop against a known/expected value before trusting `WebhookMetadata.shop`. At minimum, document clearly that only the raw body is HMAC-verified and that header-derived fields such as `shop` must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. App installs on attacker's shop `attacker.myshopify.com` and registers a webhook handler for topic `orders/create`.
2. Shopify sends a legitimate webhook to the app: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this exact request to the same endpoint but rewrites `x-shopify-shop-domain` to `victim.myshopify.com` (and/or `x-shopify-webhook-id`/`x-shopify-topic` if desired), leaving body `B` and the HMAC header untouched.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` against the header value — this still matches [1](#0-0) .
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host app processes attacker-controlled data as belonging to the victim tenant [4](#0-3) .

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
