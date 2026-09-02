### Title
Webhook shop/topic/webhook-id identity headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, and `webhook_id` values taken directly from unauthenticated HTTP headers. The identity fields the handler actually trusts (`shop`, `topic`, `webhook_id`) are never part of the signed material, so they can be altered without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string: [2](#0-1) 

`Registry.process` checks only this body-bound HMAC, then builds the `WebhookMetadata` passed to the handler using `request.shop`, `request.topic`, and `request.webhook_id`, all of which are parsed straight from the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers with no cryptographic binding: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop header value == shop bound by HMAC`. In this implementation the equality is actually `HMAC covers raw_body only` while `handler-trusted shop/topic/webhook_id == unauthenticated header values`, i.e., the field the application logic keys tenant handling on is disjoint from the field the signature protects.

### Impact Explanation
Any party capable of obtaining one legitimately Shopify-signed webhook delivery for the app (e.g., by installing the app on their own store and triggering an event) possesses a `(raw_body, hmac)` pair that remains valid under `HmacValidator.validate` regardless of the accompanying `shop-domain`/`topic`/`webhook-id` headers. They can replay that same body+hmac while substituting the `x-shopify-shop-domain` header for a different (victim) shop, or altering `topic`/`webhook-id`. `Registry.process` will accept it as authentic and invoke the handler with attacker-chosen `shop`/`topic`/`webhook_id` values, since only the body bytes were verified. Host applications typically use `WebhookMetadata#shop` to look up that shop's session/access token and perform tenant-scoped actions (e.g., mark a subscription cancelled, revoke access, sync data) — an attacker can therefore trigger actions attributed to an arbitrary victim shop, resulting in cross-tenant access/manipulation.

### Likelihood Explanation
The attacker only needs the ability to install the target app on a store they control (or otherwise capture one valid webhook delivery) and the ability to send an arbitrary HTTP POST to the app's webhook endpoint with attacker-controlled headers — both are available to an unprivileged internet user with no need for the app's `client_secret`, an access token, or TLS interception. The library's own test suite documents that only the body is signed and the shop/topic/webhook-id headers are read independently of the signature check, confirming the gap is structural rather than incidental.

### Recommendation
Bind the identity headers into the signed material verified for webhooks, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signature (e.g., include them in `to_signable_string`, or require the host app to independently confirm `shop` against a known/installed shop list before trusting `WebhookMetadata#shop`). At minimum, document prominently that `shop`/`topic`/`webhook_id` are unauthenticated and must not be used as sole tenant-selection keys without additional verification (e.g., cross-checking against the shop associated with the resolved webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), receiving a POST with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker resends this exact `(B, H)` pair to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally alters `x-shopify-topic`/`x-shopify-webhook-id`).
3. `HmacValidator.validate` recomputes the HMAC over `B` only (per `Request#to_signable_string`), matches `H`, and returns `true`.
4. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...))`, causing the host application's webhook handler to execute logic for `victim-shop` using attacker-supplied topic/body, despite the request never having been authenticated for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
