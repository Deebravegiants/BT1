This confirms the vulnerability path: `Registry.process` validates HMAC via `Utils::HmacValidator.validate(request)`, then dispatches the handler using `request.shop` (the `x-shopify-shop-domain` header) without that field being part of the signed payload. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop-domain` header not covered by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely with `Utils::HmacValidator.validate(request)`, which signs only the raw request body. The `shop` field that is passed to the app's `WebhookHandler` (derived from the `x-shopify-shop-domain` / `shopify-shop-domain` header) is never included in the HMAC-signed payload, so the binding "HMAC-authenticated request == the shop the handler acts on" does not hold.

### Finding Description
`Request#hmac` and `Request#to_signable_string` only compute/verify the digest over `@raw_body`: [2](#0-1) 

`Request#shop` is read directly from an unauthenticated header (`shopify-shop-domain` / `x-shopify-shop-domain`) and is not part of `to_signable_string`: [4](#0-3) 

`HmacValidator.validate` only recomputes the signature over `to_signable_string` (i.e., the body) and compares it to the supplied `hmac` header: [3](#0-2) 

`Registry.process` treats a valid HMAC as proof of the entire request's authenticity, then forwards `request.shop` — an unverified header — straight into the app-supplied `WebhookHandler` as the tenant identifier: [1](#0-0) 

Equality that should hold but doesn't: `shop_that_HMAC_authenticates == shop_the_handler_acts_on`. In reality the HMAC only authenticates `body`, while `shop` is taken from a header outside the signed material.

### Impact Explanation
Any party capable of delivering an HTTP POST to the app's registered webhook endpoint with a body/HMAC pair that was legitimately generated for shop A (e.g., replaying/relaying a webhook payload received for their own store, since the HMAC is only a function of the body and the shared `api_secret_key`, not of which shop it originated from) can substitute an arbitrary `x-shopify-shop-domain` header value B. `Registry.process` will pass this forged `shop: B` value into the handler while the HMAC check still passes, because the check never covered the shop header. If the host application's handler uses `data.shop` to select which merchant's session/access token/state to update (a documented and expected pattern, since `WebhookMetadata#shop` is the only tenant identifier surfaced by this gem), this results in the app performing shop-A-authenticated actions against, or attributing data to, shop B — a cross-tenant confusion inside the webhook processing pipeline that this gem owns end-to-end via `Registry.process`.

### Likelihood Explanation
Exploitation requires the attacker to have first legitimately received (or otherwise obtained) at least one valid `(body, hmac)` pair for any shop under the app (trivial for any merchant installing the app, since HMACs aren't shop-scoped), and requires the host app's handler to key subsequent tenant-scoped actions off `WebhookMetadata#shop` — a usage pattern this gem's own `WebhookMetadata` API encourages. No possession of `api_secret_key`, access tokens, or privileged accounts is needed; only a normal merchant/app-install-level actor is required, satisfying the unprivileged-internet-user threshold.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material verified by `Registry.process`, or otherwise cryptographically tie the shop-domain header to the HMAC — e.g., include it as part of `to_signable_string`, or require callers/host frameworks to independently verify that the shop-domain header matches an existing, provisioned session for that shop before dispatching to the handler. At minimum, document prominently that the shop header is unauthenticated and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Install the app on `shop-a.myshopify.com`; Shopify sends a legitimate webhook with body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` and the app's `api_secret_key`), plus `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (who controls delivery to the app's webhook endpoint, e.g., via a proxy/relay or by replaying the captured request) resends the same body `B` and the same `hmac` header `H`, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — this still passes because `shop` isn't part of `to_signable_string`. [5](#0-4) 
4. The handler executes `data.handle` with `shop: "shop-b.myshopify.com"`, even though the HMAC only ever proved the request originated with knowledge of a valid `(body, secret)` pair for shop A's webhook, not that it is authorized to act on shop B.

### Citations

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
