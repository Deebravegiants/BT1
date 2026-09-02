Confirmed: the gem's documented contract explicitly tells app developers to key their tenant logic off `data.shop` (`docs/usage/webhooks.md:14,26`), while `ShopifyAPI::Webhooks::Registry.process` derives that value straight from an HMAC-unprotected header and only checks the HMAC against the raw body.I have enough evidence to finalize the analog finding now.

### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which recomputes the signature over `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw request body [1](#0-0) . The `shop` value that identifies which merchant/tenant the webhook belongs to is read from the `x-shopify-shop-domain` header, which is never included in the HMAC-signed material [2](#0-1) . `Registry.process` still forwards this unauthenticated header value straight into the handler's `WebhookMetadata` as the merchant identity [3](#0-2) .

### Finding Description
The identity binding that should hold is:
`shop header value used by the handler == shop that produced the HMAC-signed body`

This equality is broken because `VerifiableQuery#to_signable_string` for webhook requests is defined as just `@raw_body` [1](#0-0) , and `HmacValidator.validate` only ever hashes `verifiable_query.to_signable_string` with the shared secret [4](#0-3) . None of the Shopify headers — including `shop-domain` — are part of the signed input.

Because the gem's own documented usage pattern instructs host apps to key tenant-scoped logic (e.g. `perform_later(shop_domain: data.shop, ...)`) directly off `data.shop` [5](#0-4) , and `Registry.process` builds `WebhookMetadata` with `shop: request.shop` immediately after HMAC validation succeeds [3](#0-2) , any request whose body+HMAC pair is valid for *some* shop using the app will be processed under whatever `shop-domain` header value is attached, regardless of which shop that HMAC/body pair actually belongs to.

An unprivileged attacker who runs their own store using the same app (a normal, unprivileged relationship to the app — no `api_secret_key`, access token, or victim credentials needed) legitimately receives real webhook deliveries containing a valid `body` + `x-shopify-hmac-sha256` pair for their own shop. They can then replay that exact `body`/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. Since the HMAC check only verifies the body was signed by the app's real secret (which it was, by Shopify, for the attacker's own shop) and never checks that the signed body corresponds to the shop header, the request passes `HmacValidator.validate` and is dispatched to the handler labeled as coming from the victim shop.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: `WebhookMetadata.shop` is the only tenant discriminator the library hands to the host application, and it is unauthenticated. Any host app that follows the documented pattern (write/update per-shop records keyed by `data.shop`, enqueue background jobs scoped to `shop_domain: data.shop`, invalidate/redact data for `data.shop`, etc.) can be made to attribute attacker-controlled webhook content (subject to whatever the attacker's own store can produce, e.g. `orders/create`, `products/update`, or the mandatory `customers/redact`/`shop/redact` payloads) to a different, victim shop. This is a cross-tenant data integrity/confidentiality violation achieved without any credential belonging to the victim or the app.

### Likelihood Explanation
The only prerequisite is operating an ordinary store that has the target app installed — something any internet user can do by installing a public app — and being able to POST to the app's known webhook callback path with custom headers, which is trivial. No secret, token, or victim-side action is required.

### Recommendation
Include the identity-relevant headers (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed material, or independently verify that the shop-domain header matches a shop the app has provisioned webhooks for using data recorded at registration time, before trusting it as the tenant identity passed to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the attacker's endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`
   - Body: `{"id": 1, ...}` signed with the app's real `api_secret_key`.
3. Attacker replays the identical raw body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but swaps the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the headers (all three required headers present) [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the secret [7](#0-6) .
5. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` and performs shop-scoped actions attributing the attacker's payload to the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
