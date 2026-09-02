### Title
Webhook cross-tenant spoofing via unauthenticated `shop-domain` header not covered by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches the handler using a `shop` value taken from an HTTP header that is never included in the HMAC-signed material. This breaks the identity binding `shop authenticated == shop acted upon`.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` by defining `to_signable_string` to return only `@raw_body`, and `hmac` from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header: [1](#0-0) [2](#0-1) 

`shop` is read from the separate `shopify-shop-domain` header, which is not part of the signed string at all: [3](#0-2) 

`Utils::HmacValidator.validate` only checks that the computed HMAC over `to_signable_string` (the raw body) matches the `hmac` value; it never binds any other header, including `shop`, into that check: [4](#0-3) 

`Registry.process` validates only this body/HMAC pair and then trusts `request.shop` (the unsigned header) to build the `WebhookMetadata` passed to the app's handler, which is typically used to route/attribute the payload to a tenant: [5](#0-4) 

Because a given Shopify app's `api_secret_key` is shared across every shop that installs the app (it is the developer app's secret, not a per-shop secret), any unprivileged internet user who installs the app on their own store will legitimately receive body+HMAC pairs signed with that same secret. Such a user can then capture a valid `(raw_body, hmac)` pair from their own webhook delivery and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only checks the body bytes against the HMAC, both of which are unchanged and valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

This is the equality that should hold but doesn't: `shop authenticated by HMAC == shop used to attribute data to a tenant`. The gem verifies bytes (the body) but lets an unauthenticated header field (`shop`) drive tenant-scoped processing.

### Impact Explanation
Any app built on this gem that uses `Registry.process`/`WebhookMetadata#shop` to select which tenant's data store to write to (a common multi-tenant pattern) can be made to ingest attacker-controlled webhook payloads under a victim shop's identity — e.g., injecting fake order/customer/inventory events, or triggering privileged automation, attributed to a shop the attacker never controls. This is a cross-tenant data injection/impersonation vector satisfying the "cross-tenant access" Critical impact category, achievable by any unprivileged user who can install the app on any shop (including a throwaway store) and replay traffic to the public webhook endpoint.

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker must be able to install the target app on some shop (often trivially available for public apps in the Shopify App Store), and (2) the attacker must capture and replay a legitimate signed webhook body while spoofing the `shop-domain` header — both are within reach of an unprivileged internet user with no special credentials, TLS interception, or social engineering. The main constraint is that the exploit works only for webhook topics/payloads the attacker can trigger from their own store, and delivery of the forged HTTP request must reach the app's webhook endpoint (typically public).

### Recommendation
Bind the `shop` (and other identity-relevant headers, e.g. `webhook-id`, `api-version`) into the value verified by the HMAC, or require the host application to cross-check `request.shop` against the shop the webhook was registered/expected for before dispatching to a handler. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted alone for tenant routing, and provide an API to validate `shop` against the caller's own tenant registry inside `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, receiving OAuth normally.
2. Shopify sends a legitimate webhook to the app, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: abc-123

   {"id":1,...}
   ```
   The attacker captures the raw body and the `x-shopify-hmac-sha256` value.
3. Attacker resends the identical body and HMAC header to the same app endpoint, but replaces the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` (unchanged) and it matches — validation passes.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the registered handler, which processes/stores data as if it came from `victim-shop.myshopify.com`, even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
