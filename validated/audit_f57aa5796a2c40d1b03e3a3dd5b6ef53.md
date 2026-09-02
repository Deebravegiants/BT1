This confirms the vulnerability. `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which signs solely `to_signable_string` = `@raw_body` [1](#0-0) [2](#0-1) . The `shop` field passed to the handler comes from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , which is never included in the HMAC computation.

### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook forgery via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` cryptographically authenticates the body bytes only. The `shop` identity that `Registry.process` hands to the app's webhook handler is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is completely outside the signed payload. Any attacker who can obtain one genuine, HMAC-valid webhook delivery (trivially available to anyone who installs the app on their own store, since mandatory/topic webhooks are delivered to every installer) can replay that same body+HMAC pair while substituting the `shop`-domain header for a victim shop, and the signature check will still pass.

### Finding Description
The relevant binding that should hold is:
`shop authenticated by HMAC == shop acted upon by the handler`

In `lib/shopify_api/webhooks/request.rb`:
- `hmac` is derived from the `hmac-sha256` header [4](#0-3) .
- `to_signable_string` — the bytes that get HMAC-verified — is only `@raw_body` [1](#0-0) .
- `shop` is read from the `shop-domain` header, independent of the body and of the HMAC [3](#0-2) .

`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received signature [5](#0-4) . Since `to_signable_string` never includes `shop`, `topic`, `api_version`, or `webhook_id`, the validator's cryptographic guarantee is scoped to "this body byte-string was produced by Shopify with a valid secret" — it says nothing about which shop or topic it belongs to.

`Registry.process` then trusts the request's `shop` header value directly to build the `WebhookMetadata` handed to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [2](#0-1) .

Attack sequence:
1. Attacker installs the app on their own shop (e.g. via a free/dev store) and receives one legitimate webhook delivery — e.g. `app/uninstalled`, `shop/redact`, or any subscribed topic — with a valid `x-shopify-hmac-sha256` header computed over that body.
2. Attacker POSTs the same raw body and the same (still-valid) HMAC header to the app's webhook endpoint, but rewrites `x-shopify-shop-domain` to a victim shop's domain.
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks the body bytes, which are unchanged.
4. `Registry.process` dispatches to the topic's handler with `shop: "victim-shop.myshopify.com"`, i.e. the app's own handler code (session lookup, data deletion for GDPR topics, order/customer processing, etc.) now operates believing the event pertains to the victim tenant, while the actual payload content is attacker-controlled.

This is the same bug class as the report's LP donation issue: a value that downstream logic treats as authoritative (`shop`) is derived from data that the authentication mechanism (HMAC) never actually covers, so an attacker can freely manipulate it without breaking the signature check.

### Impact Explanation
This crosses a tenant boundary using only a forged/replayed HTTP header — no access token, no `client_secret`, and no privileged account is required, only participation as an ordinary installer of the app on any shop (including the attacker's own). Depending on how the host application's webhook handler keys off `WebhookMetadata#shop` (session lookup, per-shop data writes/deletes, GDPR redact/data-request processing), this enables cross-tenant data manipulation, forced processing of attacker payload content under a victim shop identity, or triggering mandatory-compliance actions (`shop/redact`, `customers/redact`, `customers/data_request`) against a shop the attacker doesn't own.

### Likelihood Explanation
Likelihood is Low-to-Medium: it requires the attacker to first obtain at least one genuine HMAC-signed delivery, which is straightforward (install the app on an attacker-controlled shop), and requires the app's webhook endpoint to accept raw headers/body without additional binding (e.g. without independently confirming the shop via a signed URL path or session lookup keyed by something else). No secret material is needed.

### Recommendation
Include `shop`, `topic`, and other identity-bearing fields inside the HMAC-signed payload the same way `Auth::Oauth::AuthQuery#to_signable_string` binds `code`, `host`, `shop`, `state`, and `timestamp` together [6](#0-5) . Since Shopify's actual webhook HMAC is computed server-side over the body only (this cannot be changed unilaterally by the gem), the safer mitigation within this gem is to document/require that consumers never trust the `shop` header alone for authorization decisions, or to have `Registry.process`/`WebhookMetadata` cross-check the header-derived `shop` against an independent trust anchor (e.g. the registered webhook callback URL's expected shop, or a per-shop shared secret/session lookup) before dispatching to handlers, rather than passing the raw header value through unchecked.

### Proof of Concept
```ruby
raw_body = '{"id": 1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Step 1: attacker captures a genuine delivery for their own shop, e.g.:
legit_headers = {
  "shopify-topic" => "app/uninstalled",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# Step 2: attacker replays identical body+hmac but swaps only the shop-domain header
forged_headers = legit_headers.merge("shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes because HmacValidator only checks raw_body, never the shop header
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle receives WebhookMetadata with shop: "victim-shop.myshopify.com"
# even though the HMAC never covered that value.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
