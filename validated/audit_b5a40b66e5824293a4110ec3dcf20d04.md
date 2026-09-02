### Title
Webhook HMAC only covers the raw body, allowing forgery of the `shop-domain` and `topic` headers used for tenant/handler dispatch - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers that are never included in that signature. This breaks the intended identity binding `hmac_signed_content == content_acted_on`: the HMAC authenticates the body bytes, but the code acts on header fields that are not authenticated at all.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC over the body, then immediately trusts `request.topic` to select the handler and `request.shop` to build the metadata handed to that handler, without any check that these header values are consistent with anything cryptographically verified: [3](#0-2) 

Because `HmacValidator.validate` only recomputes the signature over `to_signable_string` (the body): [4](#0-3) 

...an attacker who can capture one legitimately-signed webhook delivery (e.g. from their own shop's webhook endpoint, or any request whose body+HMAC pair they can observe) can replay that exact body/HMAC pair while freely rewriting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers. `HmacValidator.validate(request)` will still return `true` because the signature check is only ever performed against the untouched raw body, and `Registry.process` will dispatch the (attacker-chosen) topic handler with an attacker-chosen `shop` value in the resulting `WebhookMetadata`.

This is the direct analog of the reported bug class: a value is trusted and acted upon (the tenant/topic used for routing and business-logic execution) that is not actually covered by the verification mechanism supposed to authenticate it (the HMAC), exactly as `transferFrom`'s return value was trusted without being checked.

### Impact Explanation
Host applications rely on `WebhookMetadata#shop` and `#topic` (derived straight from `Registry.process`) to decide which merchant's data to update/delete/export in response to a webhook (e.g. `shop/redact`, `customers/redact`, `orders/*`). Since these fields are not bound by the HMAC, an attacker can cause the library to attribute a validly-signed payload to an arbitrary shop domain or dispatch it to an arbitrary registered topic handler, resulting in cross-tenant data operations being performed for a shop the payload never actually originated from. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the ability to send one HTTP POST request with attacker-controlled headers and a previously-observed valid `(body, X-Shopify-Hmac-Sha256)` pair to the app's webhook endpoint — no access token, API secret, or privileged account is needed. Any of the app's own shops (or any party who can otherwise obtain one valid signed webhook body, which app developers frequently log or expose in test tooling) can supply the mismatched headers, making this readily reachable by an unprivileged internet user of the application built on top of this gem.

### Recommendation
Include the security-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signable content, or otherwise cryptographically bind them to the signed body, so that any header tampering invalidates the signature. At minimum, `Webhooks::Request#to_signable_string` should incorporate these header values (in a canonical form) alongside the raw body before being passed to `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker's own app receives a legitimately Shopify-signed webhook for `attacker-shop.myshopify.com` with topic `orders/create`, body `B`, and `X-Shopify-Hmac-Sha256: H` (where `H = HMAC(secret, B)`).
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or `X-Shopify-Topic: customers/redact`.
3. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `to_signable_string` (`= B`) only, which still matches `H`, so validation passes.
4. `Registry.process` looks up the handler for the attacker-chosen topic and invokes it with `shop: "victim-shop.myshopify.com"`, causing the host application's handler to act as though Shopify sent this event for `victim-shop`.

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
