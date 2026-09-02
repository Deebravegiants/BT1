### Title
Webhook shop-domain identity not bound by HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by validating the HMAC over the raw request body, while the `shop` (and `topic`/`webhook_id`) values used to route and attribute the webhook data are read directly from HTTP headers that are never included in the signed payload. This breaks the identity binding: `HMAC-verified bytes == raw_body` but `data acted upon (shop) != data covered by HMAC`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  and `#shop`, `#topic`, `#webhook_id`, `#api_version` are all pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e. the body only) and then immediately trusts `request.shop` to construct the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (the body) and compare it to the `hmac` header value — the `shop-domain` header plays no role in the comparison at all: [4](#0-3) 

Because the signature is computed only over the body, any request whose body was legitimately signed by Shopify for shop A (which the attacker can obtain by having their own store install the app and observing the genuine webhook POST Shopify sends them) will pass `Utils::HmacValidator.validate` unchanged even if the attacker swaps the `x-shopify-shop-domain` header to shop B before replaying it to the app's public webhook endpoint. The identity binding that should hold is:
`shop authenticated by HMAC == shop attributed to the webhook data`
but in this implementation:
`shop attributed to webhook data (header, unauthenticated) != shop bound by HMAC (never covered)`.

### Impact Explanation
This is a cross-tenant confusion: the webhook handler in the host app receives `WebhookMetadata` with `shop` set to an attacker-chosen value while the HMAC check reports success, because the check never covers that field. Any app logic that trusts `request.shop`/`data.shop` post-HMAC-validation to select which tenant's records to update (a very common integration pattern, and the one demonstrated in this library's own tests, e.g. `data.shop` used directly in `test_process_with_response_as_struct`) can be tricked into writing/mutating data intended for shop A into shop B's context, or vice versa — a cross-tenant access/data-integrity violation without any credential beyond public network access to the app's webhook endpoint.

### Likelihood Explanation
The prerequisite is modest: the attacker needs any single shop where the app is (or can be) installed, so they can capture a legitimate, validly-HMAC-signed webhook body/signature pair sent to them by Shopify, then POST that same body+signature to the app's public webhook callback with a different `x-shopify-shop-domain` header value. No `api_secret_key`, access token, or privileged account is required — only the app's own publicly documented webhook path and the ability to send arbitrary HTTP headers, which any unauthenticated internet user can do.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material, or otherwise cryptographically/authoritatively verify that the `shop-domain` header matches the tenant the HMAC was actually generated for (e.g., by including these header values in `to_signable_string`, or cross-checking against a Shopify-issued claim rather than trusting a bare header after only a body-only HMAC check). At minimum, document/require that host apps validate the shop domain from a session-token/JWT bound claim rather than the un-authenticated webhook header before acting on webhook payloads.

### Proof of Concept
1. Install/operate the target app on attacker-controlled `shop-a.myshopify.com`.
2. Trigger a webhook event (e.g. `orders/create`) so Shopify sends a real webhook POST to the app's registered callback URL, with body `B` and header `x-shopify-hmac-sha256: H` (valid signature over `B`).
3. Capture `B` and `H`.
4. Replay a POST to the same app webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: shop-b.myshopify.com` (victim shop).
5. `Utils::HmacValidator.validate` succeeds (per `lib/shopify_api/utils/hmac_validator.rb:12-31`, only `B` is hashed), and `Registry.process` dispatches to the handler with `shop: "shop-b.myshopify.com"` (per `lib/shopify_api/webhooks/registry.rb:188-200` and `lib/shopify_api/webhooks/request.rb:20-23`), letting the attacker inject data attributed to a victim tenant that passed signature verification.

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
