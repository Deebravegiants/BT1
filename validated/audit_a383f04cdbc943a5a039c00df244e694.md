This confirms the root cause. The webhook HMAC in `HmacValidator.validate_signature` at [1](#0-0)  only signs the value returned by `to_signable_string`, and for webhooks that value is exclusively the raw body: `Request#to_signable_string` returns `@raw_body` [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from unauthenticated headers [3](#0-2) . `Registry.process` verifies only the HMAC, then builds `WebhookMetadata` binding the (unverified) `shop` header to the (verified) body and dispatches it to the shop-specific handler: [4](#0-3) .

### Title
Webhook `shop` (tenant) header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb, lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` (tenant identifier), `topic`, `webhook_id`, and `api_version` values used to route and label the webhook are read from separate, unauthenticated HTTP headers that are never included in the HMAC-signed payload. This breaks the intended binding `hmac == HMAC(secret, body)` ⇒ `shop is also authentic`, when in fact `shop` is authenticated by nothing.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the caller-supplied `hmac` [5](#0-4) . For the webhook `Request` class, `to_signable_string` returns only `@raw_body` [2](#0-1) ; the `shop`, `topic`, `webhook_id`, and `api_version` accessors pull straight from the `shopify-*`/`x-shopify-*` headers with no cryptographic tie to the signed body [3](#0-2) .

`Registry.process` performs exactly one check — `Utils::HmacValidator.validate(request)` — before trusting the request, and then constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) alongside `request.parsed_body` (the authenticated body) and dispatches it to the app's handler [4](#0-3) . `WebhookMetadata` treats `shop` as first-class tenant data alongside `body` [6](#0-5) , and apps built on this gem are expected to key their persistence/business logic by `data.shop` from this struct (per the gem's own webhook processing example in docs).

The equality the gem should guarantee is:
`hmac_valid(raw_body) == true` ⇒ `shop header used for tenant routing is the shop that generated raw_body`

But the code only proves `hmac_valid(raw_body) == true` ⇒ `raw_body is unmodified`. Nothing proves the `shop` header wasn't substituted between the point the real Shopify webhook was generated (for shop A) and the point it lands at the app's HTTP endpoint. Any component that can rewrite/replay headers while preserving the (headerless) signed body — e.g., a webhook forwarding/relay proxy, a load balancer/CDN misconfiguration, or a delivery retry replayed by an unprivileged party who intercepted a genuine payload for their own shop — can cause the gem to hand a handler `WebhookMetadata` claiming an arbitrary victim `shop` value with body content the attacker fully controls (since it's their own shop's genuine webhook body). This is a direct structural analog to the audit's root cause: a value (`_localToken`/`_amount` there, `shop` here) that is acted upon downstream but excluded from the integrity check (`transferId` hash there, HMAC here).

### Impact Explanation
This is a cross-tenant data confusion vector: an app relying solely on this gem's `HmacValidator`/`Registry.process` for webhook authenticity has no guarantee that `data.shop` in `WebhookMetadata` corresponds to the shop whose data is in `data.body`. An attacker who can influence the `shopify-shop-domain` header of an otherwise validly-signed webhook (through their own legitimately triggered webhook combined with header manipulation/replay on the wire before reaching the app) can cause the app to process/store attacker-supplied body content under an arbitrary victim shop's tenant key — i.e., cross-tenant injection classified as Critical per the given impact list.

### Likelihood Explanation
Exploitation requires the attacker to be able to alter or forge the `shopify-shop-domain` (or other Shopify-prefixed) header on a request whose body carries a valid HMAC — feasible when the app sits behind a shared/misconfigured proxy, uses webhook forwarding/relay services, or logs and replays webhook payloads with edited headers, none of which require possessing the app's `api_secret_key`, an access token, or privileged access. The condition is fully within reach of an unprivileged internet user who controls at least one legitimately app-installed shop (to obtain a genuinely signed body) and a way to manipulate headers in transit to the app's webhook endpoint.

### Recommendation
Bind the tenant/topic identity into the authenticated material: either (a) include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified (this would require a protocol change on Shopify's side, so more practically) (b) have `Registry.process` cross-check the header-derived `shop` against a shop value embedded in or derivable from the verified body/context, or (c) require callers to pass the expected shop (from their own trusted session/store lookup) and assert `request.shop == expected_shop` before dispatching, rather than trusting the header value unconditionally as the tenant identifier.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com` with the target app installed; Shopify sends a genuine webhook: body `B` (e.g., `orders/create` for attacker's shop) with header `shopify-shop-domain: attacker-shop.myshopify.com` and a valid `shopify-hmac-sha256` computed over `B` using the app's shared secret.
2. Attacker (or an intermediary/relay they control before the request reaches the app's endpoint) rewrites the `shopify-shop-domain` header to `victim-shop.myshopify.com`, leaving `B` and the HMAC header untouched.
3. App receives the request and calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: tampered_headers))`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only re-computes the HMAC over `B`, per [1](#0-0)  and [2](#0-1) .
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [7](#0-6)  and invokes the app's handler, which now processes attacker-controlled body content as if it belonged to `victim-shop.myshopify.com`.

### Citations

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
