### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only the raw HTTP body: [1](#0-0) 

But the identity fields that the rest of the pipeline trusts — `shop`, `topic`, `webhook_id`, `api_version` — are all read straight from HTTP headers that are never included in the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies that the HMAC of `to_signable_string` (i.e., the raw body) matches, using the app's `api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` performs this body-only validation and then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` handed to the app's handler: [4](#0-3) 

This is the same bug class as the analog report: a field that is *acted on* (`shop`) is not *covered by the HMAC* that is checked. The equality that should hold — "the shop the HMAC vouches for" == "the shop the handler acts on" — does not hold, because the HMAC vouches only for the body bytes, not for the header-to-body binding.

### Impact Explanation
Because the signing secret (`api_secret_key`) is the same for every shop that installs a given app, any shop that has installed the app (an ordinary, unprivileged merchant/developer, e.g. via a free development store) can legitimately trigger a webhook and obtain a validly-signed `(raw_body, hmac)` pair for their own tenant. That attacker can then replay the identical body+HMAC while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header value to point at a different, victim shop. `HmacValidator.validate` still passes (it never inspects headers), so `Registry.process` invokes the app's handler as if the event genuinely originated from the victim shop. Depending on how the host application's handler uses `WebhookMetadata#shop` (e.g., to look up which merchant's records/session/access token to act on), this allows cross-tenant action injection — the classic case being an attacker forcing the app to process events "as" a shop it doesn't control. This satisfies the "cross-tenant access" High-impact criterion.

### Likelihood Explanation
Likelihood is moderate-to-high in any app that: (a) supports multiple merchants using one shared `api_secret_key` (essentially all public/embedded Shopify apps), and (b) allows any user to install the app on their own store (including free/dev stores) to legitimately obtain a signed webhook body. No access to `api_secret_key`, tokens, or TLS interception is required — only observing one's own legitimately delivered webhook request and replaying it with a modified header, which is achievable with a plain HTTP client.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise cryptographically tie the shop/topic/webhook-id to the signature — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds all relevant fields), or independently verify that `shop` matches an expected/allow-listed value the host application controls before dispatching to a handler. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` (legitimate installation, no special privilege needed).
2. Attacker triggers any subscribed webhook event on their store (e.g., updates a product), causing Shopify to send a request with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `B` and `H` (they own this request; no secret is exposed to them).
4. Attacker resends `POST <app-webhook-endpoint>` with the exact same body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally `shopify-topic`/`shopify-webhook-id` for a topic the victim shop is known to use).
5. `ShopifyAPI::Webhooks::Request#hmac` reproduces `H` from the header; `to_signable_string` returns `B`, unchanged from the original signed message, so `Utils::HmacValidator.validate` returns `true`.
6. `Webhooks::Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though `victim-shop` never sent this webhook — cross-tenant spoofed event delivered as authentic.

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
