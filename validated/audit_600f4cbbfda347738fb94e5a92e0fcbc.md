Confirmed: `lib/shopify_api/webhooks/request.rb` computes the HMAC signature strictly over `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the computed HMAC of `to_signable_string` (the raw body) matches the `hmac-sha256` header [3](#0-2) . `Webhooks::Registry.process` then trusts `request.shop` as the tenant identity and forwards it straight to the handler [4](#0-3) .

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` binds the HMAC signature only to the raw request body, but the `shop` (and `topic`/`webhook_id`) values that the host application uses to route and attribute the webhook payload are taken from separate, unsigned HTTP headers. `Utils::HmacValidator` never verifies that the `shop` header is the shop that actually produced the signed body, so the "authenticated shop" is not equal to the "shop the app acts on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#hmac` decodes the `hmac-sha256` header for comparison [5](#0-4) . `Request#shop` is read from the `shop-domain` header with no cryptographic tie to the body or the HMAC [6](#0-5) . `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it with `OpenSSL.secure_compare` against the received HMAC — this only proves the body bytes are authentic, not which shop they belong to [3](#0-2) .

`Registry.process` raises only if the HMAC over the body fails, then immediately trusts `request.shop` to build `WebhookMetadata` passed to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

The identity binding that should hold is:
`shop_that_produced_the_HMAC == shop_the_handler_acts_on`

Because the `shop-domain` header is excluded from the signed material, this equality is never enforced. An attacker who legitimately installs the target app on their own store (an unprivileged, self-service action requiring no secrets or victim compromise) will receive real Shopify webhooks addressed to their own shop, each with a valid HMAC computed over the body using the app's shared `api_secret_key`. The attacker can capture one such `(raw_body, hmac-sha256)` pair and replay it to the same public webhook endpoint, substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with an arbitrary victim shop domain. Because the header is not part of `to_signable_string`, the HMAC still validates, and the app processes the (attacker-controlled-timing, but Shopify-authored) body as if it belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion in the gem's core webhook validation primitive: any app built on this library that keys persistence, side effects, or authorization decisions off `WebhookMetadata#shop` (a documented, intended use of the field) can have data attributed to, or actions taken against, a shop the attacker does not own — using only a webhook payload the attacker legitimately received for their own store. Depending on the webhook topic (e.g., `app/uninstalled`, `shop/update`, `customers/redact`), this can corrupt or leak another tenant's data, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Medium-to-High. It requires only that the attacker (1) install the target app on their own shop to obtain one legitimately HMAC-signed webhook body, and (2) know or guess a target `*.myshopify.com` domain (not a secret). No access token, `api_secret_key`, or privileged access is needed — this is achievable by any unprivileged internet user who can self-install the app.

### Recommendation
Include the shop (and ideally topic/webhook id) in the signed material, or otherwise cryptographically bind them to the verified body, e.g. by computing the HMAC over a canonical string that includes the `shop-domain` header value alongside the raw body, and rejecting requests where the header-derived shop cannot be tied to the signature. At minimum, document and enforce that consuming applications must not trust `WebhookMetadata#shop` for tenant attribution without an independent authenticated source (e.g., looking up the webhook by `webhook_id` via the Admin API for the shop believed to own it).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` under the app's `api_secret_key`).
2. Attacker resends `POST /webhooks` to the same app endpoint with:
   - body: `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged)
   - header `x-shopify-shop-domain: victim-shop.myshopify.com` (attacker-controlled)
   - header `x-shopify-topic`: unchanged or attacker-chosen registered topic
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [7](#0-6) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes `B`'s contents as belonging to the victim shop [8](#0-7) .

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
