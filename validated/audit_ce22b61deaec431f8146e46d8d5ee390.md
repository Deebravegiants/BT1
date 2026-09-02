## Title
Webhook tenant identity (`shop-domain`) is not bound by the HMAC signature, allowing cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then trusts the unauthenticated `shop-domain` header as the tenant identity passed to the handler. Because the header is not part of the signed material, a party who owns one shop instance of the app can capture one of their own legitimately-signed webhooks and replay it with a different `shop-domain` header value to make the host application process/attribute the payload to a different (victim) tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`. `Utils::HmacValidator.validate` computes the HMAC exclusively over this signable string and compares it to the `hmac-sha256` header: [3](#0-2) 

`shop` (`request.shop`), `topic`, and `webhook_id` are pulled straight from HTTP headers and are never mixed into the signed content: [4](#0-3) 

`Registry.process` validates only the HMAC, then constructs `WebhookMetadata` using the unauthenticated `request.shop` and hands it to the app's handler as the authoritative tenant identity: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" pattern: the equality the library implicitly claims to guarantee is `hmac_valid(raw_body) == authenticated(shop, topic, body)`, but the real guarantee is only `hmac_valid(raw_body)`. Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` deliberately folds `shop` into the signed query string so the shop claim itself is authenticated — the webhook path has no equivalent binding.

Because a single Shopify app's `client_secret` (`Context.api_secret_key`) is shared across every shop that installs the app, any merchant who installs the app is handed a stream of correctly-HMAC-signed webhooks for their own shop. That merchant (an "unprivileged" party relative to other tenants of the same app) can take a genuine `(raw_body, hmac)` pair from their own shop and resend it to the app's webhook endpoint with the `shop-domain` (and/or `x-shopify-shop-domain`) header rewritten to point at a different shop. `HmacValidator.validate` still succeeds because it only checks the untouched raw body, and `Registry.process` will invoke the handler with `shop: request.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the library is supposed to enforce for webhook processing: a request is delivered to the app's handler carrying a forged tenant identity, backed by a signature that never actually attested to that identity. Depending on how the host application keys data mutations off `WebhookMetadata#shop` (e.g., updating records, triggering `shop/redact`/`customers/redact`/`customers/data_request` mandatory compliance topics, or any per-shop state), this enables cross-tenant data corruption/exfiltration attributed to the wrong shop — a High-severity cross-tenant boundary break carried entirely through this gem's own webhook verification API.

### Likelihood Explanation
Any party can install the target app on a shop they control (a normal, unprivileged onboarding flow) and thereby obtain a stream of validly-signed webhooks for that shop without needing the app's `client_secret`, an access token, or any other privileged credential. Replaying one of those bodies with a rewritten `shop-domain` header requires only basic HTTP tooling. The only requirement is that the app relies on `Registry.process`/`request.shop` (as documented) to key logic per shop, which is the intended, documented usage of this API.

### Recommendation
Bind the tenant/topic identity into the signed material the same way `AuthQuery` does for OAuth: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise verify them against Shopify-issued, cryptographically bound values) instead of trusting them as free-standing headers, so `HmacValidator.validate` can no longer be satisfied by replaying a signature computed over the body of a different, self-controlled shop.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, receiving genuine webhooks (e.g. `orders/create`) with a valid `x-shopify-hmac-sha256` header computed by Shopify over the JSON body using the app's `client_secret`.
2. Attacker captures one such `(raw_body, hmac)` pair.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the same `raw_body` and `hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim.myshopify.com"` and invokes the app's handler, which now processes attacker-supplied data under the victim's tenant identity (`lib/shopify_api/webhooks/registry.rb:188-200`).

### Citations

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
