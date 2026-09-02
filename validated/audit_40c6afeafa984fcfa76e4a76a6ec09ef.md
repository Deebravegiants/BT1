## Analysis

The `depositBribeERC20` reentrancy bug's underlying pattern is: **a field that is later trusted/acted upon is not actually covered by the cryptographic check that is supposed to protect it** (the token address wasn't bound before/during the transfer, allowing state to diverge from what was validated). The strongest structural analog in this gem is in webhook processing: the `shop` (and `topic`/`webhook_id`/`api_version`) fields are consumed by the application after HMAC "validation", but the HMAC signature covers **only the raw body**, never these header fields. [1](#0-0) [2](#0-1) [3](#0-2) 

Compare this to the OAuth `AuthQuery`, where `shop` **is** part of the signable string and thus fully HMAC-bound: [4](#0-3) . The webhook path has no equivalent binding for `shop`.

### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that body. The `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from HTTP headers and passed straight through to the handler as authenticated metadata, with no cryptographic binding to the signature that "validated" the request.

### Finding Description
The identity-binding equality this breaks is: `HMAC-verified(bytes)` should equal `bytes acted upon as belonging to shop S`. Here:

- `Request#hmac` reads `shopify-hmac-sha256` header. `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are read from separate, unauthenticated headers. [5](#0-4) 
- `Request#to_signable_string` (the value actually HMAC'd) returns only `@raw_body`. [1](#0-0) 
- `Registry.process` validates HMAC against the body only, then dispatches to the handler using `request.shop` and `request.topic` taken straight from headers, with no comparison against any expected/registered shop context. [2](#0-1) 

Because `Context.api_secret_key` (the app's client secret) is shared across *every* shop that installs the app, the HMAC only proves "this body was signed by someone holding the app's secret" — it proves nothing about which shop the event is attributed to. An attacker who is themselves a merchant (installs the app on their own store, a normal unprivileged action) can:
1. Cause Shopify to send a legitimately HMAC-signed webhook whose body they substantially control (e.g., create a product/order with attacker-chosen field values on their own store, triggering `products/create`/`orders/create`, etc.).
2. Capture that `raw_body` + valid `x-shopify-hmac-sha256` value.
3. POST the same body/HMAC pair directly to the app's public webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to a victim shop, and/or `x-shopify-topic` rewritten to any topic the app has a handler for.
4. `HmacValidator.validate` passes (body+HMAC are genuinely valid), and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim shop, with attacker-controlled body content. [2](#0-1) 

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to look up per-tenant session/state (a documented, expected usage pattern) and trusts `topic`/body without further cross-checks, an attacker can inject forged events attributed to an arbitrary victim shop — e.g., faking `app/uninstalled` to wipe another tenant's stored session, or injecting fabricated order/product data into a victim's tenant-scoped data store. This is a cross-tenant integrity/confidentiality breach reachable by any user capable of installing the app on their own store and sending an unauthenticated HTTP POST to the app's public webhook URL.

### Likelihood Explanation
Medium-High: requires only (a) attacker access to install the app on a store they control (typical for any Shopify app that isn't invite-only) and (b) the app's webhook endpoint being reachable without additional network-layer allowlisting (Shopify does not mandate IP allowlisting, and this gem provides no such check). No secret material beyond publicly observable webhook deliveries is needed.

### Recommendation
Bind the identity fields into the signed payload contract enforced by this gem: require (or internally construct) the signable string from a canonical combination of `raw_body` plus the `shop`, `topic`, and `webhook_id` headers, or otherwise require callers to supply the expected `shop`/topic and have `Registry.process` reject mismatches before dispatch. At minimum, document and enforce that host apps must independently re-verify `request.shop` against the shop associated with any correlated session before trusting the payload, since HMAC alone does not establish tenant identity in this gem's current implementation.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and triggers, e.g., orders/create with attacker-controlled body:
raw_body = '{"id": 1, "note": "malicious payload"}'

# Shopify legitimately signs this with the app's *shared* client secret:
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# 2. Attacker replays the same body/HMAC directly to the victim app's
#    public webhook endpoint, but swaps the shop-domain and topic headers:
forged_headers = {
  "x-shopify-topic" => "app/uninstalled",           # any topic app has a handler for
  "x-shopify-hmac-sha256" => Base64.encode64(hmac), # valid, since body is unchanged
  "x-shopify-shop-domain" => "victim.myshopify.com" # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac pair is genuine)
# => handler.handle receives WebhookMetadata(shop: "victim.myshopify.com", topic: "app/uninstalled", ...)
# => host app acts on this as if the victim shop uninstalled the app
``` [3](#0-2) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-33)
```ruby
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
