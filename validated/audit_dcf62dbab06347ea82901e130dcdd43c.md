Found a solid analog matching the report's underlying bug class ("field acted on but not covered by the HMAC").

### Title
Webhook `shop` (and topic/api-version/webhook-id) fields are trusted from unauthenticated headers while HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` for HMAC validation, but `to_signable_string` returns only the raw HTTP body: [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors, however, are all read directly and unauthenticated from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.): [2](#0-1) .

`Webhooks::Registry.process` validates the HMAC over the body only, and then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` object passed to the app's handler: [3](#0-2) .

This breaks the intended binding: `shop_field_verified_by_HMAC == shop_field_used_for_tenant_identification`. In reality, only the raw body bytes are authenticated; the `shop` used to key host-application logic (session lookup, per-tenant data isolation, `app/uninstalled` handling, etc.) is attacker-controllable header data.

### Impact Explanation
Because the same `api_secret_key` (the app's client secret) signs webhooks for every shop that has installed the app, an attacker who controls any shop (e.g., their own installed test store) can capture a legitimate `(raw_body, hmac)` pair for a webhook topic of their choosing, then replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim's `*.myshopify.com` domain). `HmacValidator.validate` will report the request as valid because only the body is checked: [4](#0-3) . The registry then dispatches the handler with `shop: request.shop` set to the spoofed victim domain: [5](#0-4) , causing the host app to attribute attacker-controlled webhook content to another tenant — a cross-tenant identity/authentication boundary violation.

### Likelihood Explanation
Any unprivileged actor able to install the app on a shop they control (or otherwise trigger a webhook they can observe) can obtain a valid body+HMAC pair for replay; forging the `shop-domain` header requires no secret material, only a normal HTTP POST to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and topic/webhook id, if they drive business logic) in the HMAC-signed payload validated by `to_signable_string`, or have `Registry.process`/consuming apps cross-validate `request.shop` against a shop that is independently known to be associated with the signing secret (e.g., per-shop webhook secrets, or binding shop to a previously stored session) rather than trusting the header value outright once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook (e.g. `app/uninstalled`) to a listener they control.
2. Attacker captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent for that event.
3. Attacker POSTs the exact same body and HMAC header to the target app's real webhook endpoint, replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because only the body is verified.
5. `Webhooks::Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , causing the host app to act (e.g., revoke/clear stored data) as though the event genuinely originated from the victim shop.

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
