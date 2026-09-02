### Title
Webhook shop/topic/webhook-id identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler subsequently trusts as the webhook's identity are read from unauthenticated HTTP headers that are not included in the signed payload, breaking the binding "bytes verified == bytes trusted for tenant identity."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers, none of which participate in `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., of the raw body) and then dispatches the handler using the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` values: [3](#0-2) 

`Utils::HmacValidator.validate` confirms only that the raw body was HMAC'd with the app's shared `client_secret`; it says nothing about which shop or topic that body is attributed to: [4](#0-3) 

Because the `client_secret` (and therefore the HMAC key) is the same for every shop that installs the app, any shop that has legitimately installed the app can obtain a genuinely-signed `(raw_body, hmac)` pair from a real Shopify webhook delivery to their own endpoint. That exact `(raw_body, hmac)` pair remains valid when replayed directly to the app's webhook endpoint with the `shop-domain` (and/or `topic`, `webhook-id`) headers rewritten to name a different, victim shop — the HMAC check still passes because it only covers `raw_body`, and `request.shop`/`request.topic` are trusted as-is by the handler dispatch.

This is the "field acted on but not covered by the HMAC" pattern: the identity binding `authenticated_body == attributed_shop` does not hold. Before the attack, `request.shop` is expected to equal the shop that produced/authorized the HMAC'd body; after the attacker's replay with a modified header, `request.shop` names an arbitrary shop while the HMAC still validates against the same body.

### Impact Explanation
An attacker who legitimately installs the app on their own shop (an unprivileged, self-service action requiring no special access) can trigger genuine webhook deliveries, capture the `(body, hmac)` pair, and replay it against the app's public webhook endpoint while spoofing the `shop-domain` header of any other shop. Any application logic that keys authorization, data writes, entitlement checks, or session/shop-scoped state off `WebhookMetadata#shop` (the value returned by `Registry.process`'s handler dispatch) can be fed forged data attributed to a victim tenant — a cross-tenant data/integrity issue at the trust boundary this gem is responsible for enforcing.

### Likelihood Explanation
The only prerequisite is installing the app on any shop (no privileged credentials, no access token, no `client_secret` needed) and being able to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers. Capturing a valid `(raw_body, hmac)` pair requires no special tooling — any webhook the attacker's own shop receives supplies one. This is straightforward for any unprivileged internet user who can install the target app.

### Recommendation
Bind the shop/topic/webhook identity into the verified signature rather than trusting unauthenticated headers: e.g., after validating the body HMAC, cross-check the header-derived `shop` against an out-of-band trusted source (a stored, per-shop webhook registration/session lookup) before invoking the handler, and document/enforce that `WebhookMetadata#shop` must never be trusted for authorization purposes unless independently verified against session storage.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app is subscribed to.
2. Capture the resulting POST request Shopify sends to the app's webhook endpoint, noting the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's shared `client_secret`).
3. Resend the identical body `B` and header `X-Shopify-Hmac-Sha256: H` to the same endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com` (and optionally alter `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `Utils::HmacValidator.validate` returns `true` (body/HMAC unchanged), and `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, so any app logic trusting `data.shop` now operates on the victim shop's identity despite the payload never having come from Shopify for that shop.

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
