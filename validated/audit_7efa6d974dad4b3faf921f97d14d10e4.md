### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content solely from the raw HTTP body, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. `Utils::HmacValidator.validate` only proves that the *body* was signed by the app's `client_secret`; it says nothing about which shop the header claims to be from. Any handler that trusts `request.shop` / `WebhookMetadata#shop` as the tenant boundary after HMAC validation is relying on an unverified field.

### Finding Description
`Utils::VerifiableQuery` requires only `hmac` and `to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns just the raw body, and `shop` is pulled from the `shopify-shop-domain` / `x-shopify-shop-domain` header without any cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(client_secret, to_signable_string)` and compares it to the `hmac` header — it never incorporates `shop`, `topic`, or any other header: [3](#0-2) 

`Registry.process` validates only this HMAC and then hands `request.shop` straight through to the app's handler as the authoritative tenant identity: [4](#0-3) [5](#0-4) 

**Identity binding broken:** the equality the gem is supposed to guarantee is
`shop_that_signed_the_request == shop_the_handler_acts_on`
but the actual guarantee provided is only
`some_shop_installed_this_app_and_its_secret_signed_this_body == true`.
The `shop` field is *acted on* (used to scope/attribute the webhook data to a tenant) but is *not covered by the HMAC*.

Because the same `client_secret` is shared across every shop that has the app installed, any merchant who installs the app (an "unprivileged internet user" with respect to other tenants) legitimately receives real, validly-HMAC-signed webhook deliveries to their own endpoint for their own shop. They fully control their own webhook endpoint, so they can capture the exact `raw_body` + `hmac-sha256` header Shopify sent them. They can then replay that identical body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (it only checks the body), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the victim's domain.

### Impact Explanation
This is a cross-tenant identity confusion at the library layer: the gem exposes an API (`Request#shop`, `WebhookMetadata#shop`) that documented usage treats as a trustworthy tenant key post-HMAC-validation, but the value is not actually bound to the signature. Any host application that (as intended/documented) uses `data.shop` from `WebhookHandler#handle` to look up or mutate per-shop records is exposed to cross-tenant data writes/reads driven by attacker-chosen shop values, using only a webhook they legitimately received for their own store. This matches the Critical criterion of cross-tenant access achieved purely through this gem's own verification logic.

### Likelihood Explanation
Any merchant who installs the app can trigger real webhook deliveries to their own endpoint (e.g., by performing an action that fires a subscribed topic), capture the raw body and `hmac-sha256`/`x-shopify-hmac-sha256` value, and replay it with a modified `shop-domain` header. No access to `client_secret`, access tokens, or any privileged account is required beyond a normal app installation — squarely within the "unprivileged internet user" boundary. The only constraint is that the replayed payload's `shop`-scoped semantics must be attacker-controllable/useful (e.g., generic order/product data), which is common in webhook payloads.

### Recommendation
Bind the `shop` (and ideally `topic`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body — e.g., include the shop domain in the signable string, or cross-check `request.shop` against the shop associated with the specific webhook subscription/session before invoking the handler. At minimum, document prominently that `shop` is unauthenticated and must be independently verified by the host app against its own known/installed shop list before being trusted as a tenant boundary.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures the webhook endpoint to log raw requests.
2. Shopify sends a legitimate webhook to the attacker's endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body with client_secret>`
   - Body: `{"id": 1, ...}` (attacker can influence contents by controlling their own store's data, e.g. creating an order with attacker-chosen fields)
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(client_secret, raw_body)`: [6](#0-5) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-chosen>, ...)`, and any per-shop logic in the host app (e.g., updating `victim-shop`'s order records) executes using attacker-supplied data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L4-16)
```ruby
module ShopifyAPI
  module Utils
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
