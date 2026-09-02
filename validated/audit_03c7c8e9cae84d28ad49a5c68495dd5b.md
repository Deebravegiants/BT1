This confirms the vulnerability. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is completely outside the HMAC's coverage [2](#0-1) . `Registry.process` validates the HMAC over the request (i.e., the body only) and then trusts `request.shop` to build `WebhookMetadata`, which is handed to the host app's handler as the tenant identity [3](#0-2) . Since the app's `api_secret_key` is one shared static secret for the whole app across all its shop installations, any shop that has legitimately installed the app can capture a genuinely-signed `(body, hmac)` pair from its own installation and replay it with a forged `shop-domain` header pointing to a different (victim) shop — the HMAC will still validate because the shop is never part of the signed payload.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, never including the `shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identifier passed to the app's webhook handler. Because the same `api_secret_key` is used to sign webhooks for every shop that has installed the app, any shop owner (an unprivileged, low-trust actor relative to other tenants) can capture a validly-signed webhook body from their own store and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a different, victim shop.

### Finding Description
The identity binding that should hold is:
`shop_bound_by_HMAC == shop_the_app_attributes_the_webhook_to`

In this gem:
- `Request#to_signable_string` returns `@raw_body` only [1](#0-0) .
- `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against anything in the signed body [2](#0-1) .
- `Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and compares it to the `hmac-sha256` header [4](#0-3) .
- `Registry.process` calls `HmacValidator.validate(request)` (validating only the body) and then immediately builds `WebhookMetadata` using `request.shop` as the trusted tenant identity handed to the app-provided handler [3](#0-2) .

The `api_secret_key` used to sign webhooks is one shared value per app configuration, not per shop [5](#0-4) . Consequently, the HMAC only proves "this body was signed with the app's secret" — it proves nothing about which shop the body belongs to. The `shop` value used everywhere downstream (per the documented `WebhookMetadata.shop` contract that host apps use to route/attribute webhook data [6](#0-5) , and as illustrated in the gem's own webhook docs where `data.shop` is used to key work per store [7](#0-6) ) is attacker-controllable independent of the signature check.

### Impact Explanation
This breaks the tenant-isolation boundary the gem is expected to enforce for webhook processing (cross-tenant access), which is a listed Critical-impact category. A shop that has installed the app (an ordinary, low-privileged actor with respect to other merchants using the same app) can forge webhooks that the app attributes to any other shop simply by reusing a validly-signed body they legitimately received and swapping the `shop-domain` header. Depending on the host app's use of `data.shop` (e.g., looking up/creating records keyed by shop, or driving deletion/redaction logic for `shop/redact`), this can lead to cross-tenant data corruption, spoofed events for a shop the attacker doesn't control, or triggering GDPR/mandatory webhook handling (e.g., `customers/redact`, `shop/redact`) against a victim shop's data.

### Likelihood Explanation
Likelihood is significant because the only prerequisite is having *any* shop installation of the target app (a completely unprivileged step available to any internet user who installs the app on their own store), and capturing one legitimately-delivered webhook body plus its HMAC — both of which are delivered directly to the attacker's own endpoint in the normal course of using the app. No access to `api_secret_key`, tokens, or the victim's systems is required.

### Recommendation
Bind the shop identity into the HMAC-signed material, or otherwise cryptographically tie the `shop-domain` header to the signature, e.g., include the `shop-domain` (and ideally `webhook-id`/`topic`) header values in `to_signable_string`, or validate that the shop in the header matches an out-of-band trusted value (such as a per-shop webhook secret or a shop allow-list already known to the host app) before constructing `WebhookMetadata`. At minimum, document prominently that `request.shop` is unauthenticated and must be independently verified against the app's own list of installed shops before being trusted.

### Proof of Concept
1. App has `api_secret_key = S` shared across every shop that installs it.
2. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}`, with header `x-shopify-hmac-sha256: <valid HMAC of body under S>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Registry.process` calls `HmacValidator.validate(request)` which only checks the body against the HMAC — it passes, since the body and HMAC are unmodified [8](#0-7) .
5. `WebhookMetadata.shop` is now `"victim-shop.myshopify.com"` even though the payload never had any binding to that shop [9](#0-8) .
6. The host application's handler processes/stores/acts on this data as if it legitimately came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
