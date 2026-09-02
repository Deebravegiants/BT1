### Title
Webhook `shop-domain` and `topic` Headers Are Not Covered by the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates *only* the body bytes. The `shop-domain` and `topic` values that `Registry.process` subsequently uses to route the webhook and to construct the `WebhookMetadata` handed to the app's handler come from unauthenticated HTTP headers that are excluded from the signature computation entirely.

### Finding Description
`AuthQuery#to_signable_string` (used for OAuth callback HMAC verification) deliberately includes every field of the query — `code`, `host`, `shop`, `state`, `timestamp` — in the signed string: [1](#0-0) 

By contrast, `Webhooks::Request#to_signable_string` signs only `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the HMAC at all: [2](#0-1) 

`Registry.process` verifies the HMAC and then trusts these unauthenticated header-derived values to route the event and build the metadata passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the secret — it has no visibility into headers not included in that string: [4](#0-3) 

This is the same root-cause pattern as the referenced report: two values are meant to move together as one authenticated unit, but the check only covers one of them (there, `redeemRate` vs `marketRate`; here, the signed body vs. the unsigned `shop`/`topic` headers). The identity binding that should hold is:

`authenticated_principal(hmac_over_signable_string) == shop_used_for_tenant_routing`

Since `to_signable_string` never includes `shop`, this equality is never actually checked — `Registry.process` accepts *any* `shop-domain` header value paired with an HMAC that is only proven valid for the body.

### Impact Explanation
Because the app's `api_secret_key` is shared across every shop that has the app installed, any unprivileged merchant who installs the (public) app on their own store legitimately receives webhook deliveries with a valid `x-shopify-hmac-sha256` signature computed with that same shared secret over a body they fully control (e.g. an `orders/create` payload for their own store, or even a body they crafted for a topic they can trigger). That attacker can then replay the exact same body + valid HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) to any other value. `Utils::HmacValidator.validate(request)` still succeeds because the signature only ever covered `@raw_body`. `Registry.process` then invokes the app's handler with `WebhookMetadata` claiming the event belongs to a victim shop of the attacker's choosing.

Any app logic that trusts `WebhookMetadata#shop` to select which tenant's data to read, mutate, or delete (order sync, GDPR redaction, inventory updates, uninstall cleanup, etc.) can be tricked into acting on/for a shop the attacker does not own — a cross-tenant access condition, without needing the app's `client_secret` or any credential leak.

### Likelihood Explanation
The prerequisite is only that the attacker can install the target public app on any shop they control (a standard, unprivileged action available to any Shopify merchant) and can send an HTTP POST to the app's public webhook endpoint — both trivially available to an "unprivileged internet user." No secret material or elevated access is required, only receipt of a normal webhook the attacker was legitimately sent for their own shop.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the payload before `Registry.process` uses them for routing/metadata (e.g., require the host app to independently confirm the shop against its own installed-shop store, and document that `request.shop`/`request.topic` are unauthenticated unless cross-checked). At minimum, `Webhooks::Request` and `Registry.process` should not allow header-only, HMAC-uncovered fields to determine which tenant's handler logic is invoked.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, obtaining legitimate webhook deliveries signed with the app's shared secret.
2. Attacker captures one delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
3. Attacker replays the exact same body `B` and HMAC `H` to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` alone (per `Request#to_signable_string`) and it matches `H`, so validation passes: [5](#0-4) 
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`: [6](#0-5) 
6. Any handler logic keyed on `data.shop` now operates against `victim-shop.myshopify.com` using attacker-supplied data.

### Citations

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
