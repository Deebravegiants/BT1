### Title
Webhook shop/topic identity not bound to HMAC signature enables cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are trusted and forwarded to the app's handler as the tenant/event identity. This breaks the intended identity binding: `hmac == HMAC(secret, body)` is verified, but `shop == the-shop-that-actually-sent-this-body` is never checked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read directly from request headers and are not part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the HMAC of `to_signable_string` (the body) against the secret: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, then dispatches the handler using the unauthenticated `request.shop` and `request.topic` as the tenant/event identity: [4](#0-3) 

The binding this breaks, stated as an equality: the gem verifies `hmac == HMAC(secret, raw_body)`, but the code and any downstream handler act as if `shop == "the tenant that produced raw_body"` — a claim that is never verified. Any two requests with the same `raw_body` produce the same valid HMAC regardless of which `shop-domain` header accompanies them.

### Impact Explanation
Because `shop` is not cryptographically bound to the signature, a party with access to *any* legitimate (body, HMAC) pair signed with the app's shared secret — most simply, one from their own shop's webhook delivery, since Shopify signs every subscriber's webhooks with the same `client_secret` — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header for a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-chosen) victim shop as the source of that data. Any app logic that trusts `request.shop` to select which merchant's records to update, delete, or overwrite is thereby cross-tenant confusable — data belonging to one merchant can be injected/attributed to another merchant's tenant context. This matches the Critical-impact category of cross-tenant access.

### Likelihood Explanation
Exploitation only requires being able to install the app on any (even attacker-controlled) shop to receive a validly-signed webhook body, then replaying it with a modified `shop-domain` (and/or `topic`) header — a low-privilege, unauthenticated-boundary action with no need for the app's `client_secret`, access token, or any special account.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used for HMAC verification (or otherwise independently bind them cryptographically to the payload), so that the verified signature actually authenticates the full set of values the handler relies on for tenant/event identity, not just the raw body bytes.

### Proof of Concept
1. Attacker installs the target app on their own shop (`attacker.myshopify.com`) and triggers an event (e.g., `orders/create`) so Shopify delivers a webhook to the app with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: orders/create`, a JSON body, and a valid `shopify-hmac-sha256` computed over that body using the app's real secret.
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the same `raw_body` and same `shopify-hmac-sha256`, but sets `shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body)` — this passes.
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's data>, ...)` per [5](#0-4) , causing the app to process attacker-supplied data under the victim shop's identity.

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
