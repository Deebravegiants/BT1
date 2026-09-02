This confirms the finding: the gem's `Registry.process` treats the `shop` and `topic` fields as trusted identity data even though they are sourced from HTTP headers that fall entirely outside the HMAC signature's coverage.

### Title
Webhook Shop/Topic Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate` [1](#0-0) , then immediately trusts the `shop` and `topic` values pulled from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from the `shopify-*`/`x-shopify-*` headers [3](#0-2) , but the signable string used to compute/verify the HMAC is only the raw body — `to_signable_string` returns `@raw_body`, nothing else [4](#0-3) . `HmacValidator.validate_signature` likewise only hashes `verifiable_query.to_signable_string` (i.e., the body) against the app's secret [5](#0-4) .

### Finding Description
This breaks the identity binding: **shop attributed to the webhook payload == shop whose secret produced the HMAC**. In reality, the gem only checks: **HMAC(body, api_secret_key) == received HMAC**, and separately trusts **shop = header value**, with no cryptographic tie between the two.

Because the `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop key), any user who installs the app on their own store legitimately receives webhooks whose bodies carry a valid HMAC computed with that same shared secret. An attacker who owns/controls one installation (their own shop) can:

1. Capture a legitimately Shopify-delivered webhook request to their own app instance (body + valid `x-shopify-hmac-sha256` header, computed over that specific body with the app's real secret).
2. Replay that exact request to the app's webhook endpoint, but modify only the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header to point at a victim shop that also uses the app.
3. `HmacValidator.validate` still returns `true`, because it only ever re-hashes `@raw_body` — the header values are never part of the signed material [4](#0-3) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `shop`/`topic` are the attacker-forged header values [2](#0-1) .

The gem's own documentation instructs host apps to treat `data.shop` as the authoritative tenant identifier for that event, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) , and mandatory topics such as `shop/redact` and `customers/redact` are dispatched through this same unauthenticated `shop` field [7](#0-6) . This means the library hands host applications a `shop` value it explicitly claims is "the shop domain of the webhook" (per `WebhookMetadata`/docs) [8](#0-7)  while never actually verifying that claim — the exact class of bug described in the report: a field (shop/topic) that is acted upon downstream but not covered by the authentication check (HMAC).

### Impact Explanation
This is a cross-tenant identity confusion at the library level: the gem asserts a body is authentically bound to a specific shop, but that binding is not proven, only asserted from an attacker-controllable header. Any Shopify merchant/app-installer (an "unprivileged internet user" relative to other tenants of the same app) can attribute arbitrary body content to a different shop's identity in the app's webhook processing pipeline, exactly mirroring the reported bug class of "verified bytes vs. acted-upon field" mismatch. Depending on the topic and how the host app is built on top of this contract, this can be leveraged toward cross-tenant data corruption/access (e.g., mandatory redact webhooks acting against the wrong shop, or event data being stored/attributed under a victim's shop record).

### Likelihood Explanation
Exploitation requires no special privilege beyond being a legitimate (even free/trial) installer of the target app on any shop — a capability available to any internet user who can install a public/listed app — combined with basic HTTP request crafting to replay a captured payload with a modified header. No access token, `client_secret`, or account takeover is required.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values in the material that is cryptographically bound to the HMAC, or otherwise cross-verify the header-derived `shop` against an authoritative source (e.g., validate the header shop is present in the app's already-established relationship for the webhook subscription, or require the signature to cover the full canonical request including these headers) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger any subscribed webhook (e.g. `orders/create`) so Shopify sends a real webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` for that body.
2. Intercept/replay this exact request to the app's webhook route, changing only `x-shopify-shop-domain` from `attacker-shop.myshopify.com` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only [4](#0-3)  and succeeds since the body is unchanged.
4. The registered handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` even though that shop never sent or approved this event [2](#0-1) .

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
```

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
