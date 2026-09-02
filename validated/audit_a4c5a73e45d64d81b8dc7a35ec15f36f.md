Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are excluded from the HMAC-signed content [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which checks `request.hmac` against `compute_signature(request.to_signable_string, secret)` — i.e., only the raw body is authenticated, not the shop header — and then dispatches the handler using the unauthenticated `request.shop` value as the tenant identity [3](#0-2) [4](#0-3) .

This matches the requested bug class exactly: a field (`shop`) that is acted on (used as the tenant/session key passed to the app's webhook handler) but not covered by the HMAC that is verified.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body via `Utils::HmacValidator.validate(request)` [5](#0-4) . However, `Webhooks::Request#to_signable_string` — the value that is actually HMAC-verified — returns only `@raw_body`, excluding the `shop`, `topic`, `webhook_id`, and `api_version` values, which are all taken straight from HTTP headers [6](#0-5) . The `shop` value is then trusted directly and forwarded to the app's webhook handler as the tenant identity, without any binding to the HMAC-verified content [7](#0-6) .

### Finding Description
The binding that should hold is:
`shop domain used to identify the tenant for handler.handle(...)` == `shop domain that was actually cryptographically bound to the signed payload`

In this gem, that equality does not hold. The HMAC is computed over `to_signable_string`, which is defined as just `@raw_body` for webhooks [1](#0-0) . The `shop` accessor is populated from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed content [8](#0-7) . `HmacValidator.validate` only checks `verifiable_query.hmac` against a signature computed from `to_signable_string` (the body) — it never incorporates the shop header [4](#0-3) .

Consequently, given any single legitimately-signed `(raw_body, hmac)` pair — for example one captured from a webhook the attacker's own shop received after installing the app — an attacker who controls delivery of the HTTP request to the app's webhook endpoint can substitute an arbitrary `shop-domain` header value while keeping the original `raw_body` and `hmac-sha256` header unchanged. `HmacValidator.validate` still returns `true` because the signed content (body) is untouched, and `Registry.process` proceeds to call the handler with `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-supplied shop domain [9](#0-8) .

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce: an app relying on `WebhookMetadata#shop` (the value handed to every registered `WebhookHandler`) to select or scope tenant data can be made to process a valid, HMAC-passed webhook body under a different shop's identity. Depending on how the host app persists data keyed by `shop`, this is a cross-tenant data confusion vector — data belonging to shop A can be written/processed under shop B's identity, or vice versa, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitability requires the attacker to control or influence the shop-domain header on a request delivered to the app's public webhook endpoint while keeping a valid `(body, hmac)` pair — e.g., an attacker who is a legitimate app installer (any merchant can install a public app) obtains one authentic signed webhook for their own shop, then can replay it with a forged header value if the transport layer or reverse proxy in front of the app does not independently validate the header against the source of the request. The gem itself provides no defense at this layer, since `to_signable_string` never includes `shop`.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-verified signable content, or perform an explicit secondary authentication of the shop header against Shopify (e.g., cross-checking against an active, previously-established session/shop record) before trusting `request.shop` for tenant dispatch. At minimum, document that `WebhookMetadata#shop` is unauthenticated header data and must be independently validated by host apps against known-installed shops before being used as a tenant key.

### Proof of Concept
```ruby
# Legitimate webhook received for shop "attacker-shop.myshopify.com":
raw_body = '{"id":1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com", # original
}

# HMAC over raw_body is valid and untouched.
# Attacker (or a proxy the attacker controls) rewrites only the header:
headers["x-shopify-shop-domain"] = "victim-shop.myshopify.com"

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Still passes because to_signable_string == raw_body, unaffected by the header change:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle is invoked with data.shop == "victim-shop.myshopify.com"
# even though the payload was never actually generated/signed for that shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
