Based on the analysis, this maps to the "field acted on but not covered by the HMAC" bug class in the exact way the rules envision.

### Title
Webhook `shop-domain` (and `topic`/`webhook_id`) header is trusted and acted on without being covered by the HMAC signature, enabling cross-tenant webhook confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's `client_secret`; it says nothing about the `shop`, `topic`, or `webhook_id` values, which are read straight from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`) [2](#0-1) . `Registry.process` validates the HMAC and then immediately hands the unauthenticated `request.shop` (along with `topic`/`webhook_id`) to the app's handler as trusted metadata [3](#0-2) .

### Finding Description
The identity binding that should hold is:

`shop attributed to the webhook by the handler == shop whose secret produced the HMAC over this exact request`

Because the HMAC is computed only over `raw_body` [4](#0-3) [1](#0-0) , the `shop`, `topic`, and `webhook_id` fields are bytes parsed but never verified. `Utils::HmacValidator.validate_signature` only recomputes the signature over `to_signable_string` and compares it to the header-supplied `hmac` [5](#0-4) .

Because webhook registrations in this gem are keyed globally by `topic` (not per-shop) and the handler is invoked with whatever `request.shop`/`request.topic`/`request.webhook_id` say [3](#0-2) , an unprivileged internet user who operates their own legitimate Shopify shop (shop A) can:
1. Receive a genuine webhook from Shopify for shop A with a body that is generic/predictable for the topic (e.g., an empty JSON payload `{}` for topics that carry little/no shop-specific data, or any topic whose payload the attacker fully controls, such as a `carts/update` on their own store crafted to match a victim's expected payload).
2. Capture the valid `(raw_body, hmac)` pair Shopify computed with the app's real `client_secret`.
3. Replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with the victim's shop domain (shop B) and/or a different `x-shopify-webhook-id`/`x-shopify-topic` combination that maps to a handler expecting that body shape.
4. `HmacValidator.validate` still succeeds, because it only checks the body signature, and `Registry.process` calls the topic handler with `WebhookMetadata` claiming `shop: "shop-B.myshopify.com"` even though the actual signer (Shopify, on behalf of the app) never issued this webhook for shop B [6](#0-5) .

This breaks the intended identity binding: the app is meant to trust `shop` as "the shop this HMAC-authenticated payload belongs to," but the gem never binds `shop` into the signed material, so the value is attacker-controllable in a replay scenario, letting one tenant's authenticated webhook be relabeled as belonging to another tenant.

### Impact Explanation
This is a cross-tenant data/identity confusion: an app's webhook handler (built against this gem's documented `WebhookMetadata.shop` field) can be made to process a request as if it originated from a shop the attacker does not control, potentially triggering per-shop side effects (data writes, cache invalidation, order/inventory actions, notification sends) attributed to the wrong merchant. This matches the "High" impact bucket for credential/tenant-boundary issues involving cross-tenant access via a broken authentication binding.

### Likelihood Explanation
Requires the attacker to control (own) at least one legitimate installed shop of the target app so they can obtain a validly-signed webhook body/HMAC pair, and requires a topic/body combination that is either static or attacker-shapeable and meaningful when replayed under a different shop header. This narrows exploitability to specific topics/apps, but no secret, TLS interception, or privileged account is needed—only a normal merchant install of the vulnerable app, which is an "unprivileged internet user" capability.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-supplied shop to the signed body (e.g., include the shop domain in `to_signable_string`, or require registrations/handlers to independently re-verify that the claimed shop has an active, matching session/access token before acting on the payload).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook for a topic whose payload the attacker can predict/control or that is empty (e.g., `{}`).
2. Capture the real request Shopify sent: headers include `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: <topic>`.
3. Resend the identical body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in [7](#0-6)  returns `true` because only the body is checked; `ShopifyAPI::Webhooks::Registry.process` in [3](#0-2)  invokes the handler with `shop: "victim.myshopify.com"`, demonstrating the handler acts on a shop value that was never covered by the HMAC.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
