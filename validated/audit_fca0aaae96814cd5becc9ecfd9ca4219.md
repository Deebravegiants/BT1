### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` value used to route and process the webhook is read from an unauthenticated HTTP header. This breaks the identity binding `shop-domain header == HMAC-covered data`, allowing a valid signature for one shop's webhook body to be replayed with an attacker-chosen `shop-domain` header, causing the app to attribute webhook data/actions to the wrong tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `hmac` is derived from the `hmac-sha256`/`x-shopify-hmac-sha256` header value: [1](#0-0) [2](#0-1) [3](#0-2) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the signed body: [4](#0-3) 

`Registry.process` validates the HMAC over the body (`Utils::HmacValidator.validate(request)`, which itself calls `verifiable_query.to_signable_string`, i.e. the raw body) and then unconditionally passes `request.shop` — the unauthenticated header — into the handler as the tenant identity: [5](#0-4) [6](#0-5) 

The equality that should hold is: `shop bound by HMAC == shop delivered to handler.handle`. In this gem, the HMAC only authenticates `(topic-independent) raw_body` bytes; `shop`, `topic`, `api_version`, and `webhook_id` are all header-derived and unsigned, yet `shop` is the field host applications rely on to look up the correct merchant/session and scope side effects (this is exactly the pattern flagged by the analog report: "a field acted on but not covered by the HMAC").

### Impact Explanation
Because the app's `client_secret`/`api_secret_key` is shared across every shop that has the app installed, any legitimate merchant of the app (an "unprivileged" actor relative to other tenants) can capture one authentic, HMAC-valid webhook delivery sent to their own store, then replay that exact raw body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, so `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the victim's domain even though the body was never sent, or signed, by/for that shop. Any host application that uses `data.shop` to select a session, access token, or perform per-tenant side effects (the intended and documented use of `WebhookMetadata`) will act on the victim shop using content actually generated for the attacker's shop — a cross-tenant confusion analogous to the credit-multiplier example where a value trusted for one identity is applied to another.

### Likelihood Explanation
Medium/High: exploitation requires only that the attacker control (or previously operate) some shop that has the target app installed — a normal, low-privilege position, not requiring `api_secret_key`, an access token, or any credential belonging to the victim. No TLS interception or social engineering is needed; the attacker replays their own legitimately-received webhook bytes with a forged header value, which any HTTP client can do.

### Recommendation
Bind the shop identity into the signed payload verification path instead of trusting the header value in isolation, e.g. include `shop-domain` (and `topic`) as part of the HMAC-signable material, or have the host application cross-check `request.shop` against the shop associated with the session/webhook subscription that was registered via `Registry.register`, rejecting webhooks whose header-declared shop was never registered for that topic/handler combination.

### Proof of Concept
1. App has two installs: Shop A (attacker-controlled) and Shop B (victim).
2. Shopify delivers a webhook to the app for Shop A: body `{"id":123}`, headers include `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac of body with app secret>`.
3. Attacker captures this full request, then re-sends it to the app's webhook endpoint, changing only the header to `x-shopify-shop-domain: shop-b.myshopify.com`, keeping the same body/HMAC.
4. `Registry.process` runs `Utils::HmacValidator.validate(request)` which succeeds (body/HMAC unchanged) and forwards `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", body: {"id"=>123}, ...)` to the handler, which processes attacker-supplied data as if it came from Shop B.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
