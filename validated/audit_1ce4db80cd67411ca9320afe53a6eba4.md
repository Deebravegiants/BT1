### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, but exposes `shop`, `topic`, `webhook_id`, and `api_version` as independent, unauthenticated header accessors. `Registry.process` trusts these header-derived fields (in particular `shop`) when constructing the `WebhookMetadata` passed to the host application's handler, even though they are never bound to the HMAC that `Utils::HmacValidator.validate` checks.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` [1](#0-0) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `hmac` is read from the `hmac-sha256` header [2](#0-1) [3](#0-2) . Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are read directly from separate, unsigned headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) [4](#0-3) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` — i.e., that the body matches the HMAC — and then dispatches to the handler using `request.topic` and `request.shop` taken straight from headers, with no cross-check that these header values were part of what was signed: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [5](#0-4) .

This breaks the intended binding: `hmac_valid ⇒ (body, shop, topic) all authentic`. In reality only `hmac_valid ⇒ body authentic`; `shop`/`topic`/`webhook_id` remain attacker-controlled headers as far as this gem's verification logic is concerned. `WebhookMetadata.shop` is a `T::Struct` field with no independent validation [6](#0-5) , so any host application that uses `data.shop` to select which tenant/session/access-token context a webhook body should be attributed to is relying on an unauthenticated value.

This is the same bug class as the "field acted on but not covered by the signature" pattern: exactly analogous to the OAuth `AuthQuery`, where `shop` **is** deliberately included inside `to_signable_string` alongside `code`/`host`/`state`/`timestamp` [7](#0-6) , showing the gem's own author-intended design elsewhere is to bind the shop identity into the signed payload — but this binding is missing for webhooks.

### Impact Explanation
An attacker who legitimately installs the target Shopify app on their own shop (an unprivileged internet user relative to any *other* merchant's tenant) will receive genuinely HMAC-signed webhook deliveries from Shopify for their own shop's events. Because the HMAC covers only the JSON body — not the `shop-domain` header — the attacker can replay that valid `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (only the body is checked), and `Registry.process` forwards `shop: <victim-domain>` to the handler. If the host application uses `data.shop` to look up the victim's session/offline access token, apply the webhook body's contents to the victim's tenant data, or trigger tenant-scoped side effects, this is a cross-tenant boundary crossing: forging events attributed to a shop the attacker does not control, directly through data this gem asserts as "HMAC verified."

### Likelihood Explanation
Reaching this requires only: (1) installing the target app on an attacker-controlled shop (a normal, unprivileged action any merchant can take), and (2) replaying an intercepted webhook HTTP request with one header changed. No access to `api_secret_key`, access tokens, or the app's `client_secret` is needed, since the attacker reuses a validly-signed body that Shopify itself sent them. The Registry and Request classes provide no additional shop/topic authentication, so the likelihood of successful exploitation against any host app that trusts `WebhookMetadata#shop` is high.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed payload the same way `AuthQuery` binds `shop` into `to_signable_string`, or independently verify that the `shop-domain` header matches a shop context the caller is authorized to receive webhooks for (e.g., cross-check against the topic subscription's registered shop) before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are not covered by the HMAC and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Install the target Shopify app on attacker's shop `attacker.myshopify.com`; Shopify sends a real webhook: body `{"id":123}` signed with HMAC `H` using the app's `api_secret_key`, headers include `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures this request and resends it to the app's webhook endpoint, keeping body and `x-shopify-hmac-sha256: H` unchanged, but replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only compares `H` against the HMAC of the unchanged body [1](#0-0)  — validation succeeds.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` [5](#0-4) , and the host app's handler processes attacker-supplied body content as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
