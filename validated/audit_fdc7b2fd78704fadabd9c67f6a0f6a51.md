### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant shop spoofing via webhook replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the HMAC over the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers and passed downstream as trusted, authenticated identity. `Registry.process` never checks that `request.shop` corresponds to the shop that actually produced the signed body, breaking the equality `hmac_signed_bytes == identity_used_by_handler`.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` using the app's single, app-wide `Context.api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`, and the identity fields (`shop`, `topic`, `api_version`, `webhook_id`) are pulled from headers that are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC of the body, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) as the authenticated identity of the event, handing it to the app's handler with no further binding check: [3](#0-2) 

Because `Context.api_secret_key` is the **same secret for every shop** that has the app installed (it is the app's client secret, not a per-shop secret), any valid `(raw_body, hmac)` pair legitimately generated for one shop's webhook remains a cryptographically valid pair for that exact same body regardless of which `shop-domain` header accompanies it. Nothing in `HmacValidator.validate` or `Registry.process` ties the verified signature to a particular shop.

This is precisely the "field acted on but not covered by the HMAC" identity-binding class from the report: the 2022-08-foundation bug trusted a return value (`royaltyInfo`) without checking a companion field (`royaltyAmount`); here, the code trusts a header field (`shop`) that is companion to, but excluded from, the HMAC-covered payload.

### Impact Explanation
An attacker who legitimately installs the app on their own store (an ordinary, unprivileged action available to any internet user with a Shopify account — no `api_secret_key`, access token, or insider access required) can:
1. Trigger or capture a genuine webhook delivery to their own endpoint (or via a public app's shared/logged endpoint), obtaining a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
2. Replay that exact body and HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and, if desired, `x-shopify-webhook-id`/`x-shopify-topic`) to name a different, victim merchant's shop.
3. `HmacValidator.validate` still passes because it only checks the body bytes against the shared secret, and `Registry.process` dispatches the handler with `shop: request.shop` set to the spoofed victim domain.

This constitutes cross-tenant data confusion: application logic keyed on `WebhookMetadata#shop` (e.g., updating merchant state, marking mandatory GDPR topics such as `shop/redact`, `customers/redact`, `customers/data_request` handled via this same registry) can be triggered under a victim shop's identity using attacker-controlled data. Depending on the handler implementation, this can lead to state corruption or unauthorized actions attributed to another tenant — squarely in the "cross-tenant access" Critical-impact category defined for this assessment.

### Likelihood Explanation
Moderate-to-high. No secret material is required, no rate limiting bypass is needed, and the only precondition is having (or observing) one valid signed webhook body from the app — trivially obtainable by installing the app once. The webhook endpoint is a public HTTP(S) endpoint by design (that's how Shopify delivers events), so an attacker can freely send arbitrary requests to it with forged headers.

### Recommendation
Bind the shop identity into the HMAC-verified payload instead of trusting an out-of-band header:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the bytes covered by the signature check, or
- Cross-validate `request.shop` against an independently-verified source (e.g., confirm the shop is one for which the app currently holds an active, previously-issued session/access token, and reject webhooks for shops that were never installed or have been uninstalled), or
- Track/dedupe by `webhook_id` (unique per delivery, per Shopify) and reject any request whose `(shop, webhook_id)` pair has not been seen from Shopify's actual webhook delivery infrastructure.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, obtaining a genuine webhook delivery, e.g. body `{}` for topic `shop/redact`, with header `x-shopify-hmac-sha256: <valid HMAC of "{}" under app secret>`.
2. Attacker sends a forged HTTP POST to the app's registered webhook route with:
   ```
   x-shopify-topic: shop/redact
   x-shopify-hmac-sha256: <the captured valid HMAC>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <any id>
   x-shopify-api-version: 2024-01
   Body: {}
   ```
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (headers present), `Utils::HmacValidator.validate` succeeds because it only checks the body `"{}"` against the shared app secret, and `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, as shown in: [3](#0-2) [4](#0-3) 

The app's business logic now processes an event under the victim shop's identity that was actually fabricated/replayed by the attacker.

### Citations

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
