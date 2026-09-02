### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` covers only the request body. The `shop-domain` header (exposed via `Request#shop`) and the `topic` header are never bound to that signature, yet `Registry.process` uses `request.shop` to build the `WebhookMetadata` passed to the app's handler as the identity of the shop that sent the webhook.

### Finding Description
`Registry.process` performs a single authenticity check: [1](#0-0) 

The check is `Utils::HmacValidator.validate(request)`, which computes/compares an HMAC over `request.to_signable_string`: [2](#0-1) 

`to_signable_string` is defined to be exactly `@raw_body` - it does not include the `shop-domain`, `topic`, or `webhook-id` headers: [3](#0-2) 

The identity binding the gem implicitly relies on is:
`hmac-verified bytes (raw_body) == bytes used to determine tenant identity (shop-domain header)`

That equality does not hold: `request.shop` is read directly from an HTTP header that carries no cryptographic binding to the signed payload. Because the app's `client_secret` (and therefore the HMAC secret) is the same across every shop that has installed the app, any store owner who has installed the app can capture a legitimately-signed webhook delivery for their own store (valid `raw_body` + valid `hmac-sha256`) and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop. `Utils::HmacValidator.validate` will still return `true` because the signature check never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` field is the attacker-controlled victim domain: [4](#0-3) 

Any host application that trusts the gem's HMAC check as proof of "this webhook body belongs to this shop" (a reasonable assumption given the library's own naming: `Request#shop` returning a value from an "HMAC-validated request") will process/store the payload under the wrong tenant.

### Impact Explanation
This breaks the shop-to-payload binding the whole webhook-verification API is designed to provide, letting a shop that has legitimately installed the app inject a validly-signed payload under an arbitrary other shop's identity. Because the vulnerability lets one tenant impersonate another tenant to the host application's webhook processing (cross-tenant data confusion/injection), it falls under the "cross-tenant access" critical-impact category.

### Likelihood Explanation
Exploitation only requires: (1) the attacker/merchant to have installed the app on their own store (a normal, unprivileged action any merchant can perform), and (2) the ability to send an arbitrary HTTP request with a captured `raw_body`/`hmac-sha256` pair and a forged `shop-domain` header to the app's public webhook endpoint. No access to `client_secret`, no TLS interception, and no privileged account is required — only ordinary use of the gem's documented `Registry.process`/`Request` API as intended by app developers.

### Recommendation
Bind the shop identity to the signed payload instead of trusting the header in isolation:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in `to_signable_string`, or
- Cross-check `request.shop` against an authenticated relationship the app already holds for that webhook subscription (e.g., verify the webhook was registered for that specific shop) before invoking the handler in `Registry.process`.

### Proof of Concept
1. App is installed on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a legitimate webhook with a real `raw_body` and correctly computed `X-Shopify-Hmac-Sha256` (signed with the app-wide `client_secret`).
2. Attacker replays this exact `raw_body` + `hmac-sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`; since `to_signable_string` only hashes `raw_body`, validation succeeds: [5](#0-4) 
4. `request.shop` returns `"victim.myshopify.com"` from the forged header, and the handler is invoked with `WebhookMetadata` claiming this data came from the victim shop: [4](#0-3) 
5. The host application processes attacker-supplied data as if it originated from `victim.myshopify.com`, achieving cross-tenant data confusion/injection despite a "passing" HMAC check.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
