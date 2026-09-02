### Title
Webhook `shop` Identity Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, never the shop header. Since every shop that installs an app shares the same `api_secret_key`, any merchant that has installed the app can obtain a valid `(body, hmac)` pair for their own store's webhook traffic and then submit a forged HTTP request to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header, while keeping the original body/HMAC untouched. The signature check passes because it never verifies the shop, so the host application's webhook handler is invoked believing the payload originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` is read straight from an unauthenticated header with no cryptographic binding to the signature: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the signature only against `to_signable_string` (i.e. the body), never incorporating the shop domain, topic, or webhook-id headers: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` relies solely on this HMAC check and then forwards the unauthenticated `request.shop` value directly into the handler's `WebhookMetadata`, which the host application treats as the tenant identity for the event: [4](#0-3) 

The equality that should hold but is broken: `shop_verified_by_HMAC == shop_used_by_handler`. In reality, the HMAC only proves `body_verified_by_HMAC == body`, and `shop` is taken from a completely separate, unauthenticated channel (the HTTP header) — a field acted on but not covered by the HMAC.

Contrast this with the OAuth callback path, `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` *is* included in the signable string and therefore is bound to the signature: [5](#0-4) 

This confirms the library's own design elsewhere treats `shop` as security-relevant and binds it to the HMAC — but the webhook `Request` class fails to do so.

### Impact Explanation
Because a single app has one `api_secret_key` shared across every merchant/tenant that installs it, any unprivileged internet user who can install the target app on their own (attacker-controlled) shop can:
1. Trigger or capture a legitimate webhook delivery to their own shop, obtaining a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
2. Replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain.
3. Pass `HmacValidator.validate` (since only the body is checked) and have the handler invoked with `WebhookMetadata#shop` set to the victim's domain.

This lets an attacker inject fabricated events attributed to a victim tenant into the host application (e.g. impersonating order/customer/app-uninstalled events for a shop the attacker does not control), causing cross-tenant data confusion/injection in any app that uses `data.shop` from `WebhookMetadata` to key persistence, billing, or session logic — a cross-tenant access violation.

### Likelihood Explanation
Exploitation requires only: (a) installing the app on any shop (something any merchant/attacker can do, no privileged access to the target needed), and (b) sending a crafted HTTP POST to the app's public webhook endpoint with a modified header — both trivially achievable by an unprivileged internet user with no access to the app's `client_secret`, TLS interception, or social engineering.

### Recommendation
Bind the shop identity to the signed payload before trusting it. Options:
- Extend `to_signable_string` (or a webhook-specific verification routine) to incorporate the `shop`, `topic`, and `webhook_id` header values alongside the raw body when computing/verifying the HMAC.
- Alternatively, after HMAC validation, independently corroborate the shop domain against a value obtained from a trusted, already-authenticated source (e.g., a session or app-installation lookup) before invoking the handler, rather than trusting the header value verbatim.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures (or triggers) a real webhook delivery: `raw_body = B`, `x-shopify-hmac-sha256 = H` (valid HMAC over `B` with the app's shared `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - body: `B` (unchanged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled content as if it belongs to `victim-shop.myshopify.com`. [4](#0-3) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
