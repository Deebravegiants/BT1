### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is trusted from unauthenticated headers while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, then hands the caller-supplied `shop`, `topic`, and `webhook_id` header values to the app's handler without any binding to that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` verifies the HMAC exclusively against that string: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` values are pulled directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic tie to the signed payload: [2](#0-1) 

`Registry.process` verifies only the HMAC and then forwards `request.shop`, `request.topic`, and `request.webhook_id` straight into `WebhookMetadata`, which the app handler consumes as trusted identity for the shop/topic/event: [3](#0-2) [4](#0-3) 

Because the `api_secret_key` used for webhook HMACs is a single app-wide secret (not per-shop), the signature only proves "signed by holder of the app secret" (i.e., Shopify's webhook infra), not "signed for shop X." The binding that should hold is:
`shop asserted in header == shop covered by hmac`
but the actual implementation only guarantees:
`hmac(raw_body, api_secret_key) == received_hmac`, with `shop` (and `topic`/`webhook_id`) entirely outside that signed scope.

### Impact Explanation
This breaks the identity binding between the authenticated payload and the shop attributed to it. Any party able to submit a raw body + valid HMAC pair to the app's public webhook endpoint (e.g., a merchant replaying/relaying their own legitimately-signed webhook body while substituting the `shopify-shop-domain` header) causes `Registry.process` to invoke the handler with attacker-chosen `shop`/`topic`/`webhook_id` metadata that was never actually verified. Downstream app logic that keys per-tenant state (e.g., uninstall handling, billing, subscription/plan updates, feature toggles) off `WebhookMetadata#shop` can be manipulated to act against a victim shop's tenant record using attacker-supplied body content, since the header fields are not covered by the same-origin proof the HMAC provides. This is a cross-tenant identity-binding bypass through the gem's documented webhook-processing API (`Registry.process`), not a misuse of an undocumented feature.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and the ability to obtain one legitimately-signed webhook body (trivial for any merchant with the app installed on their own store, since Shopify signs webhooks for all shop events with the same app secret). No access token, `client_secret`, or privileged credential is required beyond what any installed merchant already has via normal Shopify webhook delivery.

### Recommendation
Bind the shop (and ideally topic/webhook_id) identity into the signed material, or otherwise verify the header-derived `shop` against an independently authenticated source (e.g., look up the webhook by `webhook_id` server-side via the Admin API rather than trusting the header, or include shop/topic in the signable string if Shopify's webhook signing scheme is extended to support it). At minimum, document that `WebhookMetadata#shop`/`topic`/`webhook_id` are unauthenticated and must not be used for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers an event, receiving a legitimately Shopify-signed webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid for `B` under the app's shared `api_secret_key`), header `x-shopify-shop-domain = attacker.myshopify.com`.
2. Attacker replays the same `raw_body = B` and `x-shopify-hmac-sha256 = H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain = victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `hmac(B, api_secret_key) == H`, unaffected by the header change: [5](#0-4) 
4. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the app's handler acts on `victim`'s tenant record using attacker-controlled body `B`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
