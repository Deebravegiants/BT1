## Finding

The webhook signature check only binds the HTTP body to the app's secret; the `shop` value the library hands to the app's handler comes from a header that is never covered by that HMAC. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is not bound to the HMAC that authenticates the request body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that the HMAC in the `X-Shopify-Hmac-Sha256` header matches a signature computed over the raw body, using `Utils::HmacValidator.validate(request)`. The `shop` identity that the library then hands to the app's handler is read from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, which is never included in the signed material (`Request#to_signable_string` returns only `@raw_body`). The same is true for `topic`, `webhook_id`, and `api_version`. This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the HMAC proves the body came from Shopify (for *some* shop with this app installed), but does not prove which shop it came from.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the request: [3](#0-2) 

For webhooks, `Request#to_signable_string` returns only the raw HTTP body: [4](#0-3) 

`Request#shop` is derived independently from an HTTP header, outside the signed data: [5](#0-4) 

`Registry.process` treats HMAC validity as sufficient authorization to trust `request.shop` and pass it straight into the app-facing `WebhookMetadata`: [2](#0-1) 

Consequently, any party who can present *any* validly-signed body for the merchant's app (e.g. a merchant that has installed the app and thus legitimately receives webhooks with a valid HMAC for their own shop, or anyone who can otherwise obtain one HMAC/body pair, since the HMAC is independent of the shop header and identical bodies commonly recur, e.g. `{}` for many topics) can pair that valid `(body, hmac)` with an arbitrary `shop-domain` header. The registry's HMAC check passes, and `WebhookMetadata.shop` is set to the attacker-chosen shop domain, not the shop that actually generated the payload. Any handler that keys storage, billing, entitlement, or cross-tenant business logic off `data.shop` (which is exactly the intended usage pattern per the webhook docs) can be made to attribute another tenant's webhook activity to a shop the attacker controls, or vice versa — breaking the shop-identity binding across tenants.

### Impact Explanation
This breaks the `shop authenticated` == `shop the payload is attributed to` binding across tenants without requiring `api_secret_key`, an access token, or TLS interception — an attacker only needs one legitimately-received, validly-HMAC'd webhook body (trivially obtainable by installing the target app on their own shop, or observing any webhook with a static/empty body shared across shops) and control over the header of their own replayed request to the app's public webhook endpoint. This is a cross-tenant identity-binding bypass, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Moderate-to-high: many webhook topics carry minimal or empty bodies (e.g. `{}` for `app/uninstalled`-style payloads, as used in this repo's own tests), so a single legitimately-installed app instance can harvest a `(body, hmac)` pair valid for a given app and then submit it with a forged `shop-domain` header. No secret material is needed by the attacker.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) headers into the signed material verified by `Utils::HmacValidator`, or otherwise cryptographically bind them to the HMAC (e.g., include them in `to_signable_string`, matching how `AuthQuery#to_signable_string` already includes `shop`/`host` alongside the other OAuth fields). At minimum, document clearly that `WebhookMetadata.shop` is not authenticated by the HMAC and must not be trusted for cross-tenant authorization decisions, and encourage/require host apps to verify `shop` independently (e.g. against known/installed shops) before trusting it.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, and receives a legitimate webhook (e.g. `app/uninstalled`) with body `{}` and a valid `X-Shopify-Hmac-Sha256` header computed by Shopify using the app's `client_secret`.
2. Attacker sends a POST to the app's webhook endpoint with the same body `{}` and the same valid HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the request (all required headers present); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` (`{}`) — it matches, since the body and HMAC pair is genuinely valid for this app.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...))`, causing the app to process/act as though `victim-shop.myshopify.com` sent this webhook, even though it did not.

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
