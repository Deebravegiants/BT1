Confirmed: `Webhooks::Request#to_signable_string` only returns `@raw_body` [1](#0-0)  while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers, unauthenticated by the HMAC [2](#0-1) . `Registry.process` accepts the request as valid based solely on this body-only HMAC check and then dispatches to the handler using the unauthenticated `request.shop`/`request.topic` fields [3](#0-2) .

### Title
Webhook shop/topic identity not bound to HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body alone, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` values used by `Registry.process` to route and attribute the webhook are taken directly from HTTP headers that are never included in the signed content.

### Finding Description
`HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it (constant-time) against the `hmac` value returned by the query object [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac` decodes the `hmac-sha256` header [5](#0-4) .

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled unmodified from request headers (`shopify_header`) with no cryptographic binding to the HMAC-signed body [6](#0-5) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` — verifying body integrity — and then constructs `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic` to decide which handler runs and what tenant/topic the payload is attributed to [3](#0-2) .

This breaks the intended identity binding: `hmac-verified body == body authorized for the shop/topic asserted in headers`. Concretely, the equality that should hold is `signed_content ⊇ {shop, topic}`, but here `signed_content = {raw_body}` while `{shop, topic}` are asserted separately and trusted at face value.

Because the `api_secret_key` used for the HMAC is a single per-app secret shared across every shop that has installed the app (not shop-specific), any entity capable of obtaining one genuine, validly-signed webhook body/HMAC pair for the app (e.g., a merchant who installed the app and can observe webhook deliveries to their own endpoint, or replay a captured delivery) can resubmit that same `(raw_body, hmac)` pair to the app's webhook endpoint with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a different, victim shop. `Registry.process` will accept it as valid (the body HMAC checks out) and hand the handler a `WebhookMetadata` claiming it belongs to the victim shop.

### Impact Explanation
If the host application's webhook handler trusts `data.shop` to select which merchant's records to create/update/delete (the documented and expected usage pattern for this gem's `WebhookMetadata`), an attacker who has legitimate access to one shop's webhook stream can inject data attributed to a different tenant, i.e., cross-tenant data corruption/leakage — one of the explicitly in-scope Critical impacts (cross-tenant access).

### Likelihood Explanation
Requires the attacker to already have (or be able to capture) one valid signed webhook payload delivered to their own installed instance of the app — realistic for any merchant/user who installs the app themselves, since Shopify sends them real webhooks with valid HMACs computed from the app-wide secret. No access to `api_secret_key` itself is needed; only observation/replay of one legitimate delivery and the ability to alter unauthenticated headers when forwarding the request to the app's public webhook endpoint.

### Recommendation
Bind the routing identity to the HMAC-verified content: incorporate `shop`, `topic`, and `webhook_id` into the string that is HMAC-verified (or independently validate that they match values obtained through an authenticated channel, such as a prior OAuth-established shop/session record) before dispatching to handlers. At minimum, cross-check `request.shop` against a known/registered shop for the app before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), receiving a POST with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `api_secret_key`.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally alters `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `shop` is `victim-shop.myshopify.com` despite the body actually originating from the attacker's own shop [8](#0-7) .

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
