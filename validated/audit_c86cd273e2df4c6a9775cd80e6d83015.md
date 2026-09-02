### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted for tenant/handler dispatch but are not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC, but the HMAC only covers the raw request body, while the shop identity, topic, and webhook id used to dispatch and label the processed data are taken from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are derived purely from HTTP headers and are never included in the signed payload: [2](#0-1) .

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only verifies `to_signable_string` (i.e., the raw body) against the HMAC secret: [3](#0-2)  and [4](#0-3) . After this check passes, the code immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` that is handed to the app's handler, which uses `shop` to attribute the webhook event to a tenant: [5](#0-4)  and [6](#0-5) .

The identity binding that should hold is: `shop header value == shop that authorized/produced the signed body`. Because the signature only binds the raw body, this equality is never enforced by the library - `HMAC_valid(raw_body) == true` says nothing about which shop's header accompanied that body. Any request whose raw body has a previously-valid HMAC (e.g., a webhook payload the requester legitimately received for their own store) can be resent with an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header, and `Registry.process` will accept it as authentic and dispatch it to the handler labeled with the attacker-chosen shop.

### Impact Explanation
This breaks the tenant/shop identity binding at the boundary between an authenticated webhook body and the shop it is attributed to. Any downstream host application that keys persistence, side effects, or authorization decisions off `WebhookMetadata#shop` (as documented/expected usage of this gem) can be made to process or store data under the wrong tenant, i.e. cross-tenant data confusion, using only a webhook body that the requester itself legitimately possesses (e.g., from their own store's genuine webhook delivery). This matches the "Critical - cross-tenant access" impact category, since the binding broken is exactly the shop-authenticated-vs-shop-acted-upon pattern called out as in-scope.

### Likelihood Explanation
Likelihood depends on: (1) the webhook receiving endpoint being reachable by an unprivileged internet user (webhook endpoints are typically public HTTP endpoints by design, since Shopify calls them over the internet), and (2) the attacker being able to obtain at least one raw body + valid HMAC pair, which is straightforward for an unprivileged Shopify merchant/developer receiving legitimate webhooks for their own store. No access token, `api_secret_key`, or privileged account is required - only a webhook delivery the attacker already legitimately received.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed/verified material, or independently verify that the `x-shopify-shop-domain` header corresponds to the shop associated with the session/registration being processed, before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and subscribes to a webhook topic (e.g., `orders/create`).
2. Shopify sends a legitimate webhook to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, and some `raw_body`.
3. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only checks the HMAC over `raw_body`: [3](#0-2) .
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim.myshopify.com"` and dispatches it to the app's handler, causing the host app to process attacker-controlled body data as if it belonged to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L192-199)
```ruby
          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

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
