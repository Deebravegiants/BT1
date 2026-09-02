### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant event spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The gem's webhook authenticity check validates only the raw request body against the app's shared `client_secret`, while the `shop` (tenant) identity attached to the event is read from an unsigned HTTP header. Because a single app's `api_secret_key` is shared across every merchant/shop that installs the app, any shop that has legitimately installed the app can capture one of its own validly-signed webhook deliveries and replay it with the `shop` header swapped to a different (victim) tenant that uses the same app. The HMAC check still passes, and the forged shop identity is handed to the host application's webhook handler as authoritative.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers and are never part of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `computed_signature` (over `to_signable_string`, i.e. the body only) against `Context.api_secret_key`, using `OpenSSL.secure_compare`: [3](#0-2) 

`Webhooks::Registry.process` relies solely on this body-only HMAC check before trusting `request.shop` and forwarding it as the tenant identity to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop_covered_by_hmac == shop_delivered_to_handler`. Here it does not — the HMAC only vouches for the body bytes, not for the `shopify-shop-domain` header, so `shop_covered_by_hmac` is undefined while `shop_delivered_to_handler` is attacker-controllable metadata. Because `api_secret_key` is a single per-app secret shared by all shop installations (not per-tenant), a shop that legitimately receives a signed webhook for itself can reuse that exact signature with a different `shop` header value to impersonate any other tenant of the same app, without ever needing to know the secret.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), which is explicitly Critical-severity per the impact rubric. A malicious merchant using a shared app can cause the app to process/attribute webhook events (orders, app/uninstall events, GDPR events, etc.) as if they originated from a victim shop, potentially triggering data writes, notifications, or state changes scoped to the victim's tenant inside the host application — entirely from a legitimately obtained webhook signature for their own store, with no access to `api_secret_key`, tokens, or victim credentials.

### Likelihood Explanation
Likelihood is realistic for any app that has more than one shop installed (the common case for public/multi-tenant Shopify apps): any existing merchant of the app can capture their own inbound webhook HTTP request (body + `x-shopify-hmac-sha256`) using ordinary network tools, then replay it to the app's webhook endpoint with only the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed. No secret material, elevated privileges, or social engineering is required — only being an unprivileged tenant of the shared app.

### Recommendation
- Include the shop domain (and ideally `webhook_id`/topic) as part of the signed material verified against the app, or otherwise cryptographically bind the `shop` header to the specific installation/session it claims to represent (e.g., cross-check `request.shop` against a known/registered shop for that webhook subscription before trusting it).
- At minimum, document prominently that `Webhooks::Request#shop` is unauthenticated header data and must not be trusted as a tenant identifier without additional server-side verification (e.g., confirming the shop has an active session/install and that the webhook was actually registered for that shop/topic).
- Consider deduplicating/binding on `webhook_id` per shop to detect replays across tenants.

### Proof of Concept
1. App `A` is installed on shop `victim.myshopify.com` and shop `attacker.myshopify.com`, both sharing the same `api_secret_key`.
2. Attacker triggers an event on their own store (e.g., `orders/create`) and captures the resulting webhook HTTP request Shopify sends to the app, including body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` computed with the shared secret) — confirmed by construction in `lib/shopify_api/webhooks/request.rb` lines 10-13 and `lib/shopify_api/utils/hmac_validator.rb` lines 26-31, where only `B` is hashed.
3. Attacker resends the identical request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so the check passes (`lib/shopify_api/utils/hmac_validator.rb` lines 13-22).
5. `Registry.process` proceeds to build `WebhookMetadata` with `shop: "victim.myshopify.com"` and invokes the app's handler as if the event genuinely came from the victim tenant (`lib/shopify_api/webhooks/registry.rb` lines 188-200).

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
