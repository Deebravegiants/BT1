### Title
Webhook `shop`, `topic`, and `webhook-id` headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unsigned HTTP headers and passed straight through to the app's webhook handler. Because the app's webhook signing secret (the API secret key) is identical for every shop that has the app installed, an attacker who has installed the app on their own store can capture one of their own legitimately-signed webhook deliveries and replay the same `(body, hmac)` pair to the app's webhook endpoint while substituting a different value in the `x-shopify-shop-domain` header. The HMAC check still passes, and the handler receives a `WebhookMetadata` object whose `shop` attribute has been silently swapped to point at another tenant, even though only the attacker's own body content produced the valid signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from headers that are never mixed into the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `hmac` against `to_signable_string`, i.e. the body, using a secret (`Context.api_secret_key`) that is shared across all shops that install this app - it is not shop-specific: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches the request to the topic handler using the unsigned `request.shop` value directly, with no additional binding between the signed bytes and the shop the event is attributed to: [4](#0-3) 

This breaks the intended identity binding: `HMAC-covered bytes == raw_body` but the value actually acted upon for tenant identification is `shop header`, which is disjoint from what is authenticated. Any unprivileged internet user who can install the app on a store they control (a normal, unprivileged action) obtains a valid `(raw_body, hmac)` pair signed with the app-wide secret. They can then send that same pair to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value, and the library will report the event as coming from that arbitrary shop.

### Impact Explanation
Apps built on this library rely on `WebhookMetadata#shop` (sourced directly from `Registry.process`) to decide which tenant's data to update/query in response to a webhook. Since this value is unauthenticated, an attacker can inject fabricated webhook events attributed to an arbitrary victim shop, causing cross-tenant data confusion/corruption in any app that trusts this field for authorization or record lookup - matching the "cross-tenant access" Critical impact category, since the authenticated tenant (verified via HMAC secret possession) and the tenant acted upon (`shop` header) are decoupled.

### Likelihood Explanation
Any developer/attacker can freely install a public app on their own store (no privileged credentials needed) to obtain a validly-signed webhook body+HMAC pair, since the HMAC secret is per-app, not per-shop. Forging the shop header on the replay requires only sending an HTTP POST to the app's known/public webhook URL - no additional secrets are required. The primary constraint is that the forged shop value must correspond to a shop where the resulting confusion is exploitable to the attacker's benefit (e.g., an app that keys resource updates off `shop` without independently verifying it against session/API data), which is a realistic pattern for webhook consumption.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the authenticated payload rather than trusting the raw header value independently. For example, include the shop domain in `to_signable_string`, or cross-check `request.shop` against the shop stored in the app's session/authorization records associated with the delivered `webhook_id`/topic before invoking the handler, so the identity used for the HMAC and the identity acted upon are provably the same value.

### Proof of Concept
1. Install the target app (any public app using this library) on an attacker-owned development store `attacker.myshopify.com`.
2. Trigger any webhook topic the app subscribes to; capture the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify - this HMAC is computed with the app's single, shop-independent `api_secret_key`.
3. Replay this exact `(body, hmac)` pair to the app's webhook endpoint, but replace `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the (unchanged) body against the signature.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) dispatches to the handler with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the signed content originated entirely from the attacker's own shop.

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
