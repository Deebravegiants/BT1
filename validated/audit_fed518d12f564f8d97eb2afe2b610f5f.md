### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that body. The `shop` value used throughout `ShopifyAPI::Webhooks::Registry.process` (and handed to every app's webhook handler via `WebhookMetadata`) is read from the `x-shopify-shop-domain` HTTP header, which is never part of the signed data. The identity binding the gem is supposed to enforce — "the shop whose secret produced this HMAC" == "the shop the handler is told this webhook is for" — does not actually hold.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`shop` is pulled straight from a header with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` when constructing the data passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e. the raw body for webhooks) against the secret — it has no knowledge of, or dependency on, the `shop-domain` header: [4](#0-3) 

Because the HMAC only binds the body, any party who can obtain one genuinely-signed webhook body+HMAC pair for *their own* shop (which any merchant who installs the app can trivially do, e.g. by inspecting their own webhook deliveries) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value naming a *different* shop. `Utils::HmacValidator.validate(request)` still returns `true` because the signature check never touches the header, so `Registry.process` proceeds and calls the handler with `shop: request.shop` set to the attacker-chosen victim shop, together with the attacker's own (validly-signed) body.

This breaks the equality the gem's webhook processing is meant to guarantee:
`shop that produced a valid HMAC` == `shop passed to the handler / used to key sessions and data`.

### Impact Explanation
Any application built on top of this gem that uses `WebhookMetadata#shop` (or `request.shop`) to select a tenant/session, persist data, or make follow-up authenticated Admin API calls (a extremely common pattern — looking up the offline session by shop to react to a webhook) can be tricked into acting on behalf of, or writing data attributed to, a shop the attacker does not control. This is a cross-tenant confusion primitive reachable by any unprivileged party who has installed the app once (no `api_secret_key`, access token, or other credential of the target shop is required) — matching the "Critical: cross-tenant access" impact class.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-controlled shop (or otherwise obtaining one legitimately-delivered webhook body+HMAC), and (2) POSTing that exact body with a forged `x-shopify-shop-domain` header to the app's public webhook endpoint. No secrets belonging to the victim shop are needed, and the gem itself performs no additional binding between the signed bytes and the shop header before trusting it.

### Recommendation
Bind the shop identity into the verified material, e.g. include the `shop-domain` (and ideally `webhook-id`/`topic`) in the signable string used for HMAC verification, or independently verify that the shop claimed in the header corresponds to a shop with a currently active/known session before invoking handlers, so that a validly-signed body for one shop cannot be replayed under another shop's identity.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`; trigger any webhook topic the app registers (e.g. `orders/create`) and capture the raw POST body plus its `x-shopify-hmac-sha256` and other `x-shopify-*` headers.
2. Replay the exact same request to the app's webhook endpoint, keeping `x-shopify-hmac-sha256` and body untouched, but changing `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only presence is checked, not correlation with the body), `Utils::HmacValidator.validate(request)` succeeds because it only hashes `@raw_body`, and `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` alongside the attacker's payload — demonstrating the identity-binding break.

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
