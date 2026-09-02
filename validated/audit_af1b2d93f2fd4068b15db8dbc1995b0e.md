### Title
Webhook shop-domain identity binding bypass via unauthenticated header enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook using `Utils::HmacValidator.validate(request)`, but the HMAC signable string only covers the raw request body, not the `shop-domain` header that identifies the tenant. Any party that can obtain one valid `(body, hmac)` pair for the shared app `client_secret` (e.g., by installing the app on their own shop and receiving a legitimate webhook) can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` header to an arbitrary victim shop, and the signature check still passes.

### Finding Description
`HmacValidator.validate` computes `HMAC(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field via `OpenSSL.secure_compare`. [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable string and therefore carries no cryptographic binding to the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the handler using this unauthenticated `shop` value as the tenant identifier: [4](#0-3) 

The equality the gem should enforce is:
`shop bound by HMAC == shop delivered to the handler`

What is actually enforced is:
`HMAC(secret, body) == received_hmac`, independent of `shop`

Because the `client_secret` used to compute the webhook HMAC is shared across *every shop* that has the app installed (it is the app's secret, not a per-shop secret), a merchant who installs the app on their own store is a legitimate, unprivileged holder of valid `(body, hmac)` pairs for that shared secret. That merchant can capture their own genuine webhook delivery and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop's domain. The body and HMAC are untouched, so `HmacValidator.validate` still returns `true`, and `Registry.process` calls the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `shop` is now the attacker-chosen victim domain. [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity binding break: an attacker with only their own legitimate app installation (no access token, no `client_secret`, no privileged account) can forge webhook events that the host application will process as if they originated from an arbitrary other merchant's shop, while HMAC validation reports success. Any host-application logic that trusts `WebhookMetadata#shop` for tenant scoping (e.g., updating per-shop settings, triggering per-shop side effects, writing to per-shop storage keyed by `shop`) can be poisoned with attacker-controlled data under another tenant's identity — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate merchant/installer of the app (an unprivileged internet user relative to other tenants) and the ability to capture and replay one HTTP POST with modified headers, which is trivial. No secrets beyond what the attacker already legitimately possesses (their own webhook deliveries) are needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the value that is HMAC-verified for webhooks, or otherwise cryptographically bind the delivered shop domain to the payload before it is used as a tenant identifier (e.g., verify the domain against an out-of-band record of the shop associated with the calling access token/webhook subscription) instead of trusting the unauthenticated header value in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery: body `B`, header `x-shopify-hmac-sha256: H`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same POST to the app's webhook endpoint, only changing the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`, keeping body `B` and HMAC `H` unchanged.
3. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)`, which still equals `H`, so validation passes.
4. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and body `B`, causing the host application to process attacker-controlled data as belonging to the victim tenant. [6](#0-5) [7](#0-6)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
```ruby
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
