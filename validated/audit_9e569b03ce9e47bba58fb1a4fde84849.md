Confirmed. The webhook processing flow validates the HMAC over the raw body only, while the `shop-domain` header (and `topic`, `webhook-id` headers) are read separately and passed downstream to the app's handler as trusted, authenticated tenant identity — without being covered by the signature.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that body via `verifiable_query.to_signable_string`. The `shop` (`shopify-shop-domain`/`x-shopify-shop-domain` header), `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers and are never included in the signed payload, yet `ShopifyAPI::Webhooks::Registry.process` treats a passing HMAC check as proof that the *entire request*, including these headers, is authentic.

### Finding Description
`Registry.process` performs exactly one authenticity check: [1](#0-0) 

The HMAC validator only signs/verifies the raw body: [2](#0-1) [3](#0-2) 

The equality that should hold is: `shop` bound by HMAC == `shop` delivered to the handler. In this implementation, `shop` is read from `shopify-shop-domain` (an ordinary header) and handed to the handler untouched: [4](#0-3) [5](#0-4) 

Because every shop that installs the same public app shares the same `Context.api_secret_key`, any merchant who has legitimately installed the app can capture a real, validly-signed webhook delivery for their own shop (body + valid HMAC digest), then resend that identical body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` (and `topic`/`webhook-id`) headers with an arbitrary victim shop's domain and topic. `HmacValidator.validate` will still pass, because it only checks the body against the shared secret, and `WebhookMetadata.shop` will report the attacker-chosen victim domain to the app's handler.

### Impact Explanation
This is a cross-tenant identity confusion: an app that stores or acts on webhook data keyed by `data.shop` (as the documentation explicitly instructs — e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to associate attacker-supplied body content with a victim shop it does not actually originate from, or to have events attributed to shops the attacker doesn't control processed as if legitimate. This crosses a tenant boundary using only a legitimate app installation on the attacker's own shop (no access token or `client_secret` theft required), qualifying as cross-tenant access.

### Likelihood Explanation
Any unprivileged user who can install the target public app on their own store (or who otherwise has network access to trigger a webhook for their own shop) can capture a valid body+HMAC pair for a webhook topic they control, then freely replay it against the app's public webhook endpoint with forged `shop-domain`/`topic` headers. No secret material beyond what the attacker already legitimately has (a working install) is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise bind the shop domain) into the signed material verified by `HmacValidator`, or perform out-of-band verification that the `shop-domain` header matches a shop with an active app installation/session before dispatching to the handler, matching how the OidcKeyRegistry fix bound previously-unchecked structural properties (bit length, parity) directly into the verified value rather than trusting adjacent unverified metadata.

### Proof of Concept
1. Install the target public app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a real Shopify webhook delivery, capturing the raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(shared_client_secret, B)`).
2. Send a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com` and (optionally) any registered `x-shopify-topic`.
3. `HmacValidator.validate` (checking only `B` and `H`) returns `true`; `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled content as authentic data for `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
