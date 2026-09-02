### Title
Webhook shop identity (`shop-domain` header) is not covered by the HMAC signature, enabling cross-tenant event spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from an HTTP header, while the HMAC signature that authenticates the webhook only covers the raw request body. This breaks the identity binding `authenticated_bytes == bytes_used_for_tenant_attribution`, allowing an unprivileged party who can obtain one valid `(body, hmac)` pair (e.g., by installing the app on their own development/test shop, which is normal, unprivileged self-service) to replay that exact body/HMAC pair while substituting an arbitrary victim shop domain in the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates only that the HMAC of the raw body matches (`Utils::HmacValidator.validate(request)`), then immediately forwards `request.shop` — taken from the header, never covered by the signature — to the app's handler as authoritative tenant identity: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the app's single, shop-independent `api_secret_key`: [4](#0-3) 

Because a single app secret is shared across every shop that installs the app, any user can install the app on their own shop, receive a legitimate webhook with a valid body+HMAC pair, and then resend that identical body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` header to a victim shop's domain. `Registry.process` will pass HMAC validation (since only the body is checked) and will hand the handler a `WebhookMetadata` claiming the event originated from the victim shop: [5](#0-4) 

The gem's own documentation instructs handler authors to trust `data.shop` directly to decide which shop's data to act on (e.g. enqueue background jobs keyed by `shop_domain: data.shop`), reinforcing that this field is intended to carry tenant identity: [6](#0-5) 

This matches the described bug class: a field (`shop`) that is acted upon by the application is not covered by the cryptographic binding (`HMAC`) that is supposed to prove authenticity, so the value used for tenant attribution can be manipulated independently of the value that was actually verified.

### Impact Explanation
This allows an attacker who legitimately controls one shop that has the app installed (an "unprivileged" actor relative to any other merchant) to inject fabricated webhook events attributed to an arbitrary victim shop domain, without ever obtaining that victim's credentials or access token. Depending on what the host application does with `data.shop` in its handler (e.g., invalidate/expire sessions, mark uninstalled, update local cached order/customer/product records, trigger notifications, or gate business logic per shop), this is a cross-tenant data integrity/confusion vector — satisfying the "cross-tenant access" criterion for Critical impact, since it breaks the isolation between tenants that the webhook signing scheme is supposed to guarantee.

### Likelihood Explanation
Likelihood is meaningful but bounded by application behavior downstream: the gem itself does nothing to prevent this because it never binds `shop` (or `topic`/`webhook_id`) into the HMAC computation, and it explicitly recommends trusting `data.shop`. Any developer following the documented pattern is exposed. The attack requires only the ability to install the app on one's own shop and issue an HTTP POST to the app's own public webhook endpoint with edited headers and a captured body/HMAC pair — no secrets, tokens, or social engineering required.

### Recommendation
Bind the shop identity to the authenticated payload rather than trusting an unauthenticated header:
- Include the `shop` (and ideally `topic`, `webhook_id`) values in the HMAC-signable string, or otherwise cryptographically bind them to the body before verification, similar to how `AuthQuery#to_signable_string` includes `shop` in the OAuth callback signature.
- If per-field binding isn't feasible because Shopify's own webhook signature only signs the body, the gem should document/require that consuming apps cross-check `request.shop` against a shop with an active installation/session record before trusting it for any privileged/tenant-scoped action, and this cross-check should be surfaced as a first-class API rather than left as an unstated caller responsibility.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw HTTP request Shopify sends, including `X-Shopify-Hmac-Sha256: <hmac>` and body `{"id":1,...}`.
2. Replay this exact request to the app's webhook endpoint, but replace the header:
   `X-Shopify-Shop-Domain: attacker.myshopify.com` → `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   (keep the body and `X-Shopify-Hmac-Sha256` unchanged).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate` succeeds because it only re-computes the HMAC over the unchanged raw body using the app's single `api_secret_key`: [7](#0-6) 
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and any downstream logic keyed on `data.shop` now operates on the attacker-chosen shop identity despite the payload having originated from the attacker's own shop.

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
