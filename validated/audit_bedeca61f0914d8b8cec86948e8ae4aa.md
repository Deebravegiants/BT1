This is a solid analog to the ZetaChain bug class — a field that identity/tenant logic *acts on* is not actually covered by the cryptographic binding that's supposed to authenticate it.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` authenticates *only* the body bytes, not the `x-shopify-shop-domain` header. `Registry.process` nonetheless trusts `request.shop` (read straight from that unauthenticated header) as the tenant identity handed to the app's webhook handler.

### Finding Description
`Request#hmac` is computed from the `hmac-sha256` header, and `Request#to_signable_string` is defined as just `@raw_body`: [1](#0-0) 

`Request#shop` is derived independently from the `shop-domain` header, which plays no role in `to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant for the handler callback: [3](#0-2) 

This is exactly the identity-binding break described in the report's bug class: the field the application *acts on* for tenant scoping (`shop`) is not the field the cryptographic check actually covers (`raw_body` only). The equality that should hold — "shop authenticated == shop acted on" — is broken because the HMAC binds only the body, while `shop` is read from a sibling, unauthenticated header.

Because Shopify signs webhooks for an app using the single, app-wide `client_secret` (shared across every shop that installs the app, not a per-shop secret), any merchant — including a malicious one — can install the app and receive a genuinely, validly-signed webhook for their own store (e.g. `orders/create`). Since the `shop-domain` header is excluded from the signed content, that attacker can replay the exact same body + valid HMAC to the app's webhook endpoint while substituting a victim shop's domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass (body and HMAC are untouched and valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
Any app relying on `Registry.process`/`request.shop` (as documented and used per `docs/usage/webhooks.md` and `test/webhooks/registry_test.rb`) to determine which merchant's data record to update, create, or act on will process attacker-controlled, cross-tenant webhook events under a victim shop's identity. This is a cross-tenant access vulnerability: an unprivileged (but legitimately app-installing) attacker can inject events attributed to any other shop without needing that shop's credentials, access tokens, or `client_secret`.

### Likelihood Explanation
The prerequisite — being able to install the target app under an attacker-owned Shopify store to receive a legitimately-signed webhook — is trivial for any public/unprivileged Shopify merchant, and no possession of the app's `client_secret` or any victim credential is required. Replaying the body with a modified `shop-domain` header is straightforward once a valid signed body/HMAC pair for any topic is captured.

### Recommendation
Bind the shop domain (and ideally other identity-relevant headers such as `webhook-id`/`api-version`) into the HMAC-covered signable content, or otherwise verify `request.shop` against a value that is cryptographically committed to (e.g., have `to_signable_string` include the shop domain header, matching how Shopify's own webhook signature construction should be verified end-to-end). At minimum, document that host applications must not treat `request.shop` as authenticated unless verified out-of-band (e.g., cross-checked against a known/expected shop for that installation).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic they control content for (e.g. updates an order) and captures the resulting POST: raw body `B`, and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` using the app's `client_secret`).
3. Attacker resends the identical body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` calls `request.to_signable_string` → `B`, recomputes HMAC with the app's real `client_secret`, and it matches `H`, so validation succeeds: [4](#0-3) 
5. `Registry.process` proceeds and calls the registered handler with `shop: request.shop` equal to `victim-shop.myshopify.com`, even though the payload was authored/triggered entirely by the attacker on their own store: [3](#0-2)

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
