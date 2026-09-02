Confirmed: the `shop` field in `ShopifyAPI::Webhooks::Request` is populated purely from the unauthenticated `X-Shopify-Shop-Domain` header, while `to_signable_string` only returns `@raw_body` for HMAC verification.### Title
Webhook `shop-domain` header is not covered by HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the incoming webhook using `Utils::HmacValidator.validate(request)`, which HMACs `request.to_signable_string`. In `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while the `shop` attribute passed downstream to the app's handler is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . The HMAC therefore authenticates the body bytes but not the shop identity that the gem attaches to that body.

### Finding Description
The bug-class analog is: "a field acted on but not covered by the HMAC." The gem's own `VerifiableQuery` interface only requires `hmac` and `to_signable_string` [3](#0-2) , and `HmacValidator.validate` computes/compares the HMAC purely over `to_signable_string` with the app's `api_secret_key` [4](#0-3) . For webhooks, `to_signable_string` is `@raw_body` only — the `shop`, `topic`, `webhook_id`, and `api_version` values are taken straight from headers with zero cryptographic binding to the signature [5](#0-4) .

`Registry.process` raises only if the HMAC over the body is invalid, then immediately builds `WebhookMetadata` using the header-derived, unverified `request.shop` and hands it to the app's registered handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) . `WebhookMetadata.shop` is a plain `String` const with no further validation [7](#0-6) .

The equality that should hold but does not: `shop_bound_by_hmac == shop_delivered_to_handler`. Before the attack: a legitimate webhook for shop A has `raw_body_A` + `hmac(raw_body_A)` valid, `shop-domain: A`. After the attack: an attacker who controls one installed shop (shop A) captures this valid `(raw_body_A, hmac)` pair and replays it to the app's webhook endpoint with the header changed to `shop-domain: B` (a victim tenant of the same app). Since `to_signable_string` never includes the shop header, `HmacValidator.validate` still succeeds (the HMAC only covers `raw_body_A`, which is unchanged), and the app's handler receives `WebhookMetadata(shop: "B", body: raw_body_A's data, ...)`. The app is misled into believing shop A's webhook event/data belongs to shop B.

### Impact Explanation
This crosses a tenant boundary within a single app installation: an attacker who is a legitimate, otherwise unprivileged user of a multi-tenant app (i.e., someone who has merely installed the app on their own store, which is enough to receive genuine app webhooks signed with the shared `api_secret_key`) can cause the host application to process attacker-supplied webhook content while it believes the content originates from an arbitrary other shop. Depending on how the host app keys sessions, records, or GDPR/redaction actions off of `WebhookMetadata#shop`, this can be used to inject falsified data into a victim tenant's records, trigger redaction/data-request workflows against the wrong shop, or otherwise perform actions attributable to a shop the attacker does not control. This matches the "cross-tenant access" impact category since the shop identity used to route/attribute webhook data is not authenticated.

### Likelihood Explanation
Likelihood is Medium: the attacker needs their own valid installation of the app (any developer/merchant can install a public app), a way to receive at least one signed webhook for their own shop (any subscribed topic works, e.g. `app/uninstalled`, `shop/update`), and the ability to replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint with a modified `shop-domain` header — all of which are within reach of an unprivileged internet user with no access to `api_secret_key` or any merchant's access token.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise cryptographically/independently verify that the `shop-domain` header matches the tenant the raw body actually originates from. Concretely:
- Update `Webhooks::Request#to_signable_string` to include `shop`, `topic`, and `webhook_id` alongside the raw body, and change the app-side verification to expect this composite string, or
- Reject/flag any mismatch by cross-checking the `shop-domain` header against an independent trust signal (e.g., topic-specific expectations, or per-shop webhook secrets when available) before constructing `WebhookMetadata`.
- At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC in this gem and that host apps must not use it as a sole identity check for security-sensitive decisions — though a library-level fix that binds `shop` into the signature is the sounder remediation.

### Proof of Concept
1. Attacker installs the target app on their own store, `attacker-shop.myshopify.com`, and subscribes/receives a legitimate webhook delivery for it, e.g. `app/uninstalled`, giving the attacker a genuinely valid pair:
   - `raw_body = '{"...": "..."}'`
   - `headers["x-shopify-hmac-sha256"] = <valid HMAC over raw_body using the app's api_secret_key>`
   - `headers["x-shopify-shop-domain"] = "attacker-shop.myshopify.com"`
2. Attacker resends this exact HTTP request to the app's webhook endpoint, only changing the header:
   - `headers["x-shopify-shop-domain"] = "victim-shop.myshopify.com"`
3. `Webhooks::Request.new(raw_body:, headers:)` is constructed; `request.shop` now returns `"victim-shop.myshopify.com"` [2](#0-1) .
4. `Registry.process(request)` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`raw_body`, unchanged) and successfully matches the original, still-valid signature [8](#0-7) , [9](#0-8) .
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))` is invoked, delivering attacker-controlled body data tagged as belonging to `victim-shop.myshopify.com` [10](#0-9) .

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
