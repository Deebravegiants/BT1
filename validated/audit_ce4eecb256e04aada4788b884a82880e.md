### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, API version, and webhook ID entirely from unauthenticated HTTP headers, while the HMAC signature that `HmacValidator` checks is computed only over the raw request body. This breaks the intended binding of `hmac ⇒ (body, shop, topic)`, letting an attacker who possesses one valid `(body, hmac)` pair replay it with a forged `shop-domain` header to make the app process the webhook as belonging to a different, arbitrary tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, never the headers: [1](#0-0) 

But `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled straight from headers that are never part of what gets signed: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts this validation and then hands the *header-derived, unsigned* `shop` (and `topic`) straight to the app's handler as authenticated tenant identity: [4](#0-3) [5](#0-4) 

Because the `api_secret_key` used to sign webhook payloads is the app's single client secret shared across **every shop that installs the app**, and the body-only HMAC never binds the signature to a specific tenant, the following holds:

- Before request: `hmac = HMAC(secret, body)`, independent of `shop` header.
- Attacker action: capture (or legitimately receive, e.g. from their own installed test shop) any valid `(body, hmac)` webhook pair, then resend it to the app's webhook endpoint with `x-shopify-shop-domain` changed to a victim shop's domain (and/or `x-shopify-topic` changed).
- After request: `HmacValidator.validate` still returns `true` (it only checks `body` vs `hmac`), so `Registry.process` proceeds and invokes the handler with `WebhookMetadata(shop: "<victim-shop>", topic: "<attacker-chosen-topic>", body: <attacker-controlled or replayed body>)`.

This is the direct analog of the reported bug class: the identity-bearing field (`shop`) is *acted upon* by the code (used as tenant key when handing data to the app's handler) but is not *covered* by the cryptographic check (HMAC), exactly like a collateral-type/pool-id parameter that governs security-critical behavior but isn't validated together with the rest of the invariant.

### Impact Explanation
Any app built on this gem that relies on `WebhookMetadata#shop` (or `#topic`) from `ShopifyAPI::Webhooks::Registry.process` to route data updates per-tenant is exposed to cross-tenant data confusion: an attacker with access to one legitimate `(body, hmac)` pair (e.g., because they run their own shop with the app installed) can make the app apply that webhook's body under a different shop's identity. Depending on how the host app persists webhook data (e.g., writing order/customer data keyed by `data.shop`), this can corrupt or leak data across tenants — a cross-tenant access impact.

### Likelihood Explanation
Medium-High: the attacker only needs to be a legitimate installer of the target app (a normal, unprivileged capability for any Shopify merchant/developer) to generate a valid signed webhook body/HMAC pair from their own shop, and can freely control the `shop-domain`/`topic` headers sent in their replayed HTTP request since they are not re-validated against the signature. No secrets, tokens, or elevated access are required — only network access to the app's public webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `api_version`/`webhook_id`) in the signable string used by `HmacValidator`, or otherwise cryptographically bind the shop/topic to the HMAC (e.g., verify the resulting shop against a known allow-list of installed shops for the app, independent of the header, before trusting it). At minimum, document that consumers must independently verify `WebhookMetadata#shop` against their own tenant registry rather than treating it as authenticated purely because `HmacValidator.validate` passed.

### Proof of Concept
```ruby
# Attacker has a legitimate shop "attacker.myshopify.com" with the app installed,
# and receives a genuine webhook from Shopify:
#   body = '{"id": 1, "note": "hello"}'
#   headers = {
#     "x-shopify-hmac-sha256" => "<valid HMAC for body, signed with the shared api_secret_key>",
#     "x-shopify-topic" => "orders/create",
#     "x-shopify-shop-domain" => "attacker.myshopify.com"
#   }

# Attacker replays the exact same body + hmac, but swaps the shop-domain header:
forged_headers = {
  "x-shopify-hmac-sha256" => headers["x-shopify-hmac-sha256"], # unchanged, still valid for `body`
  "x-shopify-topic" => "orders/create",
  "x-shopify-shop-domain" => "victim-shop.myshopify.com" # attacker-controlled
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

# HmacValidator only checks body vs hmac — shop header is irrelevant to the check:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process therefore invokes the handler believing this event
# genuinely originated from "victim-shop.myshopify.com":
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", ...))
```

Note: full exploitation impact depends on how the consuming application uses `WebhookMetadata#shop`; this PoC demonstrates that the gem itself provides no binding between the verified bytes (`raw_body`) and the trusted tenant identifier (`shop` header), which is the root cause enabling any such downstream cross-tenant impact.

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
