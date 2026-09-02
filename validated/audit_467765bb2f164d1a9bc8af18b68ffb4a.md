Found a valid analog: Shopify webhook delivery identity fields (`shop`, `topic`, `webhook-id`, `api-version`) are read straight from HTTP headers and are never covered by the HMAC signature verification, yet `ShopifyAPI::Webhooks::Registry.process` trusts them to route to a handler and to populate the `shop`/`topic` metadata the handler acts on.

### Title
Webhook `shop`/`topic` identity headers are not bound to the HMAC signature, enabling cross-shop/cross-topic webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read verbatim from arbitrary HTTP headers with no cryptographic binding [2](#0-1) . `Registry.process` validates only that HMAC-over-body [3](#0-2) , then dispatches based on the unauthenticated `topic` header and forwards the unauthenticated `shop` header straight into the handler's `WebhookMetadata`.

### Finding Description
The intended invariant is: `hmac_valid(body, secret) == true` should imply the entire delivery — including which shop and which topic it is claimed to represent — is authentic. In reality the equality that holds is only `hmac_valid(body, secret) == true`; the `shop` and `topic` fields are outside that binding. Because a public Shopify app shares one `api_secret_key` across all installations, any party who installs the app on their own (freely creatable) development store receives at least one legitimately signed `(raw_body, hmac)` pair. That pair remains valid under `HmacValidator.validate` regardless of what `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers accompany it, since `to_signable_string` never includes them [1](#0-0) . The attacker can therefore resend the identical body+HMAC with the `shop` header rewritten to a victim's `*.myshopify.com` domain and/or the `topic` header rewritten to any topic the app has a handler for [3](#0-2) , causing the handler to process data it believes came from the victim shop/topic.

### Impact Explanation
This crosses a tenant boundary: `WebhookMetadata.shop` is the value host applications typically use as the lookup key for shop-scoped session/state records [4](#0-3) . A handler that trusts this field (e.g., for `app/uninstalled`, `shop/redact`, or state-resetting topics) can be triggered against an arbitrary victim shop by an attacker who only controls their own store's installation — this is cross-tenant impact.

### Likelihood Explanation
Requires only: (1) installing the target public app on a store the attacker controls (no special privilege), (2) capturing one legitimate webhook delivery to that store, and (3) sending a forged HTTP POST directly to the app's public webhook endpoint with altered headers. No access to `api_secret_key`, tokens, or victim credentials is needed.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed material (or independently verify them against records associated with the still-active session/access-token for that shop) before acting on them in `Registry.process`, rather than trusting header values that fall outside `to_signable_string`.

### Proof of Concept
1. Install the target app on attacker-controlled dev store `attacker.myshopify.com`; capture a delivered webhook `raw_body` B and its valid `x-shopify-hmac-sha256` header H (computed by Shopify with the shared `api_secret_key`) [5](#0-4) .
2. POST to the app's webhook endpoint with body B, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim.myshopify.com` and `x-shopify-topic: <target-topic>`.
3. `HmacValidator.validate` passes because it only checks `Digest.hexencode(...)` against B [6](#0-5) ; `Registry.process` looks up the handler by the forged topic and invokes it with `shop: "victim.myshopify.com"` [3](#0-2) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
