### Title
Webhook shop/topic/version identity fields are unauthenticated (excluded from HMAC signature) enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `shop-domain`, `topic`, `webhook-id`, and `api-version` headers when dispatching to the app's handler. Because the HMAC signature never binds these header fields, an attacker who can obtain any one valid `(body, hmac)` pair can replay it with an arbitrary `shop-domain` header and have it accepted as an authentic webhook for a different, victim tenant.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` value from the request: [1](#0-0) 

For webhooks, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [2](#0-1) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read straight from HTTP headers, which are entirely outside the signed payload: [3](#0-2) 

`Registry.process` validates only the HMAC and then uses the unauthenticated `request.shop` (and other header-derived fields) to build the `WebhookMetadata` passed to the app's handler as the tenant identity for that event: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unauthenticated `String` field consumed by host applications as the source of truth for "which shop does this event belong to": [5](#0-4) 

The broken identity binding is: `shop header trusted by handler == shop bytes actually covered by HMAC`. In reality, `shop header trusted by handler != {}` (the empty set of bytes covered by the signature), since the signature covers only `@raw_body`.

Because the signature is independent of the headers, any entity capable of producing one valid `(body, hmac)` pair — for example the operator of their own store with the app installed, who legitimately receives real webhook deliveries with a valid HMAC computed from the shared `client_secret` — can capture that body+HMAC pair and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to point at an arbitrary victim shop domain (and, if useful, a different `x-shopify-topic`/`x-shopify-webhook-id`/`x-shopify-api-version`). `HmacValidator.validate` still succeeds because it never inspects the headers, and the handler is invoked believing the event originates from the victim shop.

### Impact Explanation
This breaks the tenant/shop identity boundary that multi-tenant Shopify apps rely on to route webhook data to the correct merchant's records. A host application that keys its persistence, cache invalidation, order/product reconciliation, or entitlement logic off `WebhookMetadata.shop` can be tricked into attributing another shop's data changes to a shop the attacker doesn't own, or into acting on attacker-supplied payloads under the identity of a shop chosen by the attacker — a cross-tenant data integrity/confidentiality issue purely through this gem's own webhook-verification API, with no access token or `client_secret` ever needed by the attacker.

### Likelihood Explanation
Any user with a Shopify store where the target app is installed automatically receives legitimately HMAC-signed webhook deliveries as part of normal app operation. Capturing one `(body, hmac)` pair requires no privileged access — it is simply intercepted from a webhook request the attacker's own shop naturally triggers (e.g., a `products/create` event on their own dev/trial store). Replaying it against the app's public webhook endpoint with a modified `shop-domain` header is a single HTTP request with no cryptographic secret required.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `api-version`, and ideally `webhook-id`) in the signable payload used for HMAC verification, or otherwise cryptographically bind the shop domain to the signed body (e.g., verify it against a shop the app knows currently has this webhook subscription/topic registered) before constructing `WebhookMetadata` and invoking the handler. At minimum, document prominently that `WebhookMetadata.shop`/`topic`/`webhook_id` are unauthenticated and must not be used as sole tenant-identity determinants without additional server-side cross-checks (e.g., confirming an active session/installation exists for that shop).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and triggers any webhook-producing action (e.g., creates a product). Shopify delivers a webhook request with body `B` and a valid header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker captures `B` and `H` (e.g., via their own logging/proxy — no special privilege beyond owning a shop).
3. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - body = `B` (unchanged)
   - `x-shopify-hmac-sha256` = `H` (unchanged)
   - `x-shopify-shop-domain` = `victim-shop.myshopify.com` (changed)
   - `x-shopify-topic` = same or different registered topic
4. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`, which calls `Utils::HmacValidator.validate(request)`; since `to_signable_string` returns only `B`, validation succeeds.
5. `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` is passed to the registered handler, which processes attacker-controlled data under the victim shop's identity. [6](#0-5) [7](#0-6)

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

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
