### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) header is trusted for tenant attribution but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload as the raw HTTP body only, while the shop identity used downstream to attribute the webhook to a merchant is read from a separate, unsigned header. This breaks the equality `hmac_valid(body) == shop_header_is_authentic`, letting an attacker who controls one legitimately-signed webhook body (via their own shop's installation of the app) replay it against the app's webhook endpoint with an arbitrary victim `shop-domain` header and have it accepted as authentic.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

but `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers that are never part of the signed material: [2](#0-1) 

`HmacValidator.validate` verifies exactly and only `verifiable_query.to_signable_string` (the body) against the HMAC secret: [3](#0-2) 

`Registry.process` gates only on this body-HMAC check, then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which is the struct the host application's handler is documented and expected to use to identify which merchant/tenant the payload belongs to: [4](#0-3) [5](#0-4) 

The identity binding the gem is supposed to enforce is: `hmac_valid(raw_body) => (topic, shop, webhook_id, api_version) are authentic for that body`. In reality the HMAC signs only `raw_body`, so the equality `signed_bytes == bytes_the_handler_trusts_for_tenant_attribution` does not hold — `shop` (and the other three headers) are trusted but not bound to the signature, exactly the class of bug described in the analog report (a field acted on but not covered by the integrity check).

### Impact Explanation
The app's `client_secret` (`api_secret_key`) is a single, per-app secret shared across every shop that installs the app — it is not per-tenant. Any unprivileged internet user can install the target app on their own (even a free development) store and thereby legitimately receive Shopify-signed webhooks whose `X-Shopify-Hmac-Sha256` is computed with that same shared secret. Because the HMAC never covers the `shop-domain` header, that attacker can take a legitimate `(body, hmac)` pair from their own shop and resend it to the app's public webhook endpoint with the `shop-domain` header rewritten to point at a victim merchant. The HMAC check in `HmacValidator.validate` still passes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-authored) body belongs to the victim shop. Any host application that uses `data.shop` to select the tenant record to update (the intended and documented use of the field) will process attacker-controlled data under the victim's identity — cross-tenant data injection/impersonation via the webhook channel.

### Likelihood Explanation
Reaching this requires only: (1) the ability to install the target app on an attacker-controlled shop — a normal, unprivileged action for any Shopify merchant/developer, and (2) capturing one's own genuine webhook delivery, which the app itself sends to the attacker's own registered endpoint. No access to `api_secret_key`, access tokens, or any privileged account is needed. This is squarely reachable by an unprivileged internet user through the gem's own webhook-processing code path (`Registry.process` / `HmacValidator.validate` / `Webhooks::Request`).

### Recommendation
Include the `shop-domain`, `topic`, `webhook-id`, and `api-version` header values in the HMAC-signed material (or otherwise cryptographically bind them, e.g., derive/validate `shop` against a value covered by the signature) so that `to_signable_string` reflects everything the handler will trust, not just the raw body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify delivers a genuine webhook to the app's endpoint with headers including a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared `client_secret`.
3. Attacker captures `raw_body` and `X-Shopify-Hmac-Sha256` from this legitimate delivery.
4. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the HMAC (`request.rb` `to_signable_string` returns `@raw_body`, unaffected by the swapped `shop-domain` header).
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)` and, following the gem's documented API, processes the attacker's data as if it originated from the victim shop.

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
