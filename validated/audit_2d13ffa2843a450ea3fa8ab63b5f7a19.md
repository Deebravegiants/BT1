This confirms the vulnerability: `WebhookMetadata.shop`, `topic`, `webhook_id`, and `api_version` are all populated from HTTP headers, and the `to_signable_string` used for HMAC verification only covers `@raw_body`, none of these header-derived fields.### Title
Webhook shop-domain (and topic/id/api-version) not covered by HMAC allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, but the HMAC that `Registry.process` validates only signs the raw request body. This breaks the identity binding `hmac(body) == hmac(body)` from the field that host applications actually trust for tenant attribution: `request.shop`. An attacker who can obtain one valid `(body, hmac)` pair (e.g., from their own store's legitimate webhook delivery) can replay that same body/HMAC while substituting the `shopify-shop-domain` header for a victim shop, and the signature check still passes.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery`'s HMAC by recomputing the signature over `to_signable_string` and comparing it to the supplied `hmac`: [1](#0-0) 

For webhooks, `Webhooks::Request#to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-controllable HTTP headers, independent of the signed bytes: [3](#0-2) 

`Registry.process` validates the HMAC and then hands the header-derived `shop` (along with `topic`, `webhook_id`, `api_version`) straight to the application's `WebhookHandler`, without any check that `shop` was part of what was signed: [4](#0-3) 

`WebhookMetadata` — the struct handed to every registered handler — carries this unauthenticated `shop` field as if it were verified: [5](#0-4) 

Because `to_signable_string` is only `@raw_body`, the HMAC proves the body wasn't tampered with, but it proves nothing about which shop, topic, webhook id, or API version the request is attributed to. This exactly matches the "field acted on but not covered by the HMAC" bug class: the equality that should hold is `hmac_signed_shop == request.shop`, but no such binding exists — `hmac` only signs `body`.

### Impact Explanation
Any unprivileged actor who operates their own Shopify store receives genuine, correctly-signed webhook deliveries from Shopify for their own shop. Because the signature covers only the body, that same `(raw_body, hmac)` pair remains valid when replayed with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header changed to a victim's shop domain — `HmacValidator.validate` will still accept it. If the host application (as this gem's own `WebhookMetadata` API encourages) uses `data.shop` to select which merchant's session/data store to act on, an attacker can inject events attributed to an arbitrary victim shop, causing cross-tenant confusion/cross-tenant access to another merchant's webhook-triggered logic (e.g., triggering `shop/redact`, `customers/redact`, or app-specific business logic against a tenant that never sent that event). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app author following this gem's documented pattern (using `WebhookMetadata#shop` for tenant routing) because the gem provides no warning or binding between the verified bytes and the `shop`/`topic`/`webhook_id` fields it exposes. An attacker only needs the ability to install the app on their own store (unprivileged, self-service) to harvest a valid `(body, hmac)` pair, then send a crafted HTTP request to the app's public webhook endpoint with a substituted shop header — no access token, `client_secret`, or privileged account required.

### Recommendation
Include the tenant/topic identity fields in the signed payload verification, or otherwise bind them cryptographically to the HMAC before trusting them:
- Extend `Webhooks::Request#to_signable_string` (or add a secondary check in `Registry.process`) to incorporate `shop`, `topic`, and `webhook_id` into what's verified, or
- Require the host application to cross-check `request.shop` against a known/registered shop for the given webhook subscription before acting on it, and document this requirement clearly since the gem's own `WebhookMetadata` struct currently presents `shop` as if it were trustworthy.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g. `orders/create`) to the app's registered endpoint, capturing the raw body `B` and its valid header `shopify-hmac-sha256: H` (computed by Shopify over `B` using the app's `client_secret`).
2. Attacker crafts a new POST to the same webhook endpoint using the exact same body `B` and `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` and any desired `shopify-webhook-id`/`shopify-topic` values.
3. `Webhooks::Request.new` accepts the request (all required headers present) and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`= B`) and matches `H` — validation succeeds because `shop`/`topic`/`webhook_id` were never part of the signed string: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and any application logic keyed off `data.shop` now operates as though the event legitimately originated from the victim shop.

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
