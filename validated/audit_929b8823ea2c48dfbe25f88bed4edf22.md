### Title
`shop` field trusted from unauthenticated header while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity passed to app handlers from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature verified by `Utils::HmacValidator` covers only the raw request body, never the shop header. This breaks the intended identity binding `verified(hmac) == trusted(shop)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read directly from an attacker-controllable HTTP header with no cryptographic binding to the signature: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, then unconditionally forwards `request.shop` to the app's handler as authenticated tenant context: [4](#0-3) 

`HmacValidator.validate` computes the digest strictly from `verifiable_query.to_signable_string` (i.e., the body only) and compares it to the `hmac` header value — it never incorporates `shop`: [5](#0-4) 

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` *is* explicitly included in `to_signable_string` and therefore is bound to the HMAC that Shopify computes for OAuth callbacks: [6](#0-5) 

The webhook path lacks this equivalent binding: the `shop` value that reaches `WebhookMetadata` (and thus the app's business logic, e.g. `perform_later(shop_domain: data.shop, ...)` as shown in the gem's own docs) is never covered by the signature that `process` checks. [7](#0-6) [8](#0-7) 

The broken equality is: `hmac_verified(raw_body)` ≠ `shop_trusted(header["shopify-shop-domain"])`. An attacker who controls (or has previously received, e.g. by installing the app on their own store) any body+HMAC pair that passes verification can freely substitute the `shopify-shop-domain` header value to any other shop domain string, since that header is not part of the signed material, and `Registry.process` will accept it and dispatch it to the handler labeled with the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged attacker who has one valid (body, hmac) pair for a webhook delivered to their own installation can forge a request that the app will process as belonging to a different, victim shop (`request.shop` is fully attacker-controlled while `HmacValidator.validate` still returns `true`). Depending on how the host application implements the handler (as the gem's own documentation directs — keying background jobs, data records, or session lookups off `data.shop`), this can cause the app to associate attacker-supplied webhook data with a victim shop's tenant context, corrupting per-shop data isolation. This matches the "cross-tenant access" class of Critical impact defined in the rules, since the tenant/session boundary (`shop`) is not actually authenticated by the HMAC that gatekeeps webhook processing.

### Likelihood Explanation
Likelihood is moderate-to-high for any unprivileged internet user with access to at least one legitimately-signed webhook body (trivially obtainable by installing the app on their own free/dev shop and capturing any webhook Shopify sends them, since the HMAC secret is shared across all shops for a given app). No access to `api_secret_key`, tokens, or privileged accounts is required — only observation of one's own legitimate webhook traffic and the ability to POST a modified header to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`) values into the material that is authenticated before they are trusted for tenant-identification purposes:
- Have `Utils::HmacValidator`/`Request#to_signable_string` incorporate the shop-domain header into the signed string comparison, or
- After HMAC validation, require the host application to independently confirm that `request.shop` corresponds to a shop with an active, previously-established session/installation before acting on the payload, and document this requirement prominently, since Shopify's own webhook HMAC by design covers only the body.
- At minimum, update `docs/usage/webhooks.md` and `WebhookMetadata` to explicitly flag that `shop` is unauthenticated and must be independently validated against known installed shops by the consuming app before being used as a tenant key.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives a legitimate webhook, e.g. orders/create, with a valid HMAC
# computed by Shopify over the raw body using the app's shared secret.
captured_body = '{"id":1,"note":"hi"}'
captured_hmac_b64 = "<value Shopify sent for attacker's shop>"

# Attacker now replays the SAME body+hmac but swaps only the
# shopify-shop-domain header, which is not covered by the signature.
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => captured_hmac_b64,       # still valid for captured_body
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)

# HmacValidator.validate only checks HMAC(captured_body) == captured_hmac_b64,
# which still holds, so this call succeeds and the handler is invoked
# with data.shop == "victim-shop.myshopify.com".
ShopifyAPI::Webhooks::Registry.process(request)
```
`Registry.process` accepts the forged request because `Utils::HmacValidator.validate` only checks the body against the HMAC and never checks `request.shop`: [9](#0-8)

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
