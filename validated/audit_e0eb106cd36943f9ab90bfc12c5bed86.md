### Title
Webhook `shop-domain` (and other Shopify headers) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `HmacValidator.validate` checks in `Registry.process` covers *only* the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are never part of the signed material, yet they are the values the gem hands to the host application's webhook handler as the authoritative tenant/event identity.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

which returns `@raw_body` only. `Registry.process` verifies the webhook using exactly this signable string: [2](#0-1) 

and then constructs `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id` — all parsed straight from headers with no cryptographic binding: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only recomputes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header: [4](#0-3) 

This is the same class of defect as the reported bug: a value that is *acted on* (here, the `shop` identity passed to the handler) is not covered by the integrity check that is supposed to bind it (the HMAC), i.e. `shop_trusted_by_handler != shop_bound_by_hmac`. Since the `api_secret_key` is shared across all shops installed on a given app, a byte-for-byte valid `(raw_body, hmac)` pair obtained from any one shop's webhook delivery remains valid when replayed with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header swapped to a different, victim shop. `Registry.process` will accept it, and the handler will receive `WebhookMetadata` claiming the body originated from the victim shop.

### Impact Explanation
This breaks the tenant/identity boundary the gem is documented to provide to consumers of `Registry.process`/`WebhookMetadata` — the `shop` field is the mechanism by which host applications determine which merchant's data/session to act on. An attacker who has observed or produced one valid signed webhook body (e.g., by triggering an event on a shop they control, or where a previously-delivered payload leaks) can replay it to the app's public webhook endpoint with an arbitrary `shop-domain` header and have it accepted as an authentic event for a different, unrelated tenant — a cross-tenant confusion/spoofing condition.

### Likelihood Explanation
Exploitation only requires the ability to POST to the app's public webhook endpoint (no secret, token, or privileged account needed) plus possession of one previously valid `(raw_body, hmac)` pair, which is trivial to obtain by installing the app on an attacker-controlled shop and receiving one legitimate webhook, or observing one in transit/logs. No cryptographic material needs to be broken; only the unsigned header is altered.

### Recommendation
Include the identity-binding fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable material used for HMAC verification, or otherwise cryptographically bind the header-derived `shop` to the signed body (e.g., verify the shop domain against a value obtained from an authenticated source rather than an unauthenticated header) before constructing `WebhookMetadata` and dispatching to the handler.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`, independent of shop).
2. Replay the exact same request to the app's webhook endpoint, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` only checks `HMAC(api_secret_key, B) == H`, which still holds, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) accepts the request.
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's body content, even though the event never occurred on the victim shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
