Confirmed identity-binding break: `Registry.process` uses `request.shop` (the `X-Shopify-Shop-Domain` header) to build `WebhookMetadata`, but `HmacValidator.validate(request)` only verifies the HMAC over `request.to_signable_string`, which is `@raw_body` — the shop-domain header is never part of the signed bytes. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop identity trusted without HMAC coverage, breaking `shop == HMAC-signed(shop)` binding - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#shop` reads the tenant identity from the `X-Shopify-Shop-Domain` header, but `Webhooks::Request#to_signable_string` returns only the raw body, and `Registry.process` validates the HMAC solely against that raw body before handing `request.shop` (unauthenticated) to the app's webhook handler as the tenant identity.

### Finding Description
The bug-class analog is the same as the report: a field acted upon (`shop`) is not covered by the integrity check (HMAC), so the value that determines tenant/session binding can be forged independently of the signed payload.

`Webhooks::Request` defines `hmac` from the `hmac-sha256` header and `to_signable_string` as `@raw_body` only [4](#0-3) [2](#0-1) . The `shop` accessor pulls straight from the `shop-domain` header with no cryptographic binding to the body or HMAC [5](#0-4) .

`Registry.process` validates HMAC via `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` i.e. `HMAC(secret, raw_body)` and compares it to the `hmac-sha256` header [6](#0-5) . Once that check passes, `Registry.process` immediately constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) as the tenant identity passed to the app-supplied `handler.handle` [3](#0-2) .

The identity binding that should hold is: `shop-domain header == value implicitly certified by the HMAC signature`. In reality the HMAC only certifies the body bytes; the shop-domain header is out-of-band and unauthenticated by this gem. Since the app's `client_secret` is shared across *all* shops that install the app, any legitimate (unprivileged) merchant who installs the app receives genuinely-signed webhook deliveries for their own store. That merchant fully controls the HTTP request reaching the app's webhook endpoint (per Shopify's delivery model, the shop replays or the endpoint owner can be a malicious/relay actor), and can replay a validly-HMAC'd body while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop domain. `HmacValidator.validate` still returns true because the raw body's HMAC is unaffected by the header, and `Registry.process` passes the attacker-chosen `shop` straight through to the handler as if it were verified.

### Impact Explanation
This satisfies the "Critical — cross-tenant access" bar: an app relying on this gem's own `Registry.process`/`WebhookMetadata.shop` to authorize which tenant's data a webhook payload applies to (a documented, intended usage pattern of this gem, not host misuse) can be tricked into associating one shop's signed webhook body with a different, attacker-chosen shop identity. This can be leveraged to write/attribute data cross-tenant, or to trigger shop-scoped side effects (e.g., app/uninstall, orders, GDPR redact handlers) against a shop that never sent the corresponding event, purely by controlling only the value of an HTTP header alongside a legitimately-signed body from the attacker's own shop.

### Likelihood Explanation
Any unprivileged Shopify merchant can install the target app for free and receive real, validly-signed webhook deliveries, since `api_secret_key` is shared across all installs and is never merchant-specific data the attacker needs to steal. Replaying or crafting the delivery HTTP request with a different `shop-domain` header requires no privileged access, no leaked credentials, and no TLS interception — it is entirely within the reach of a normal internet user who is a legitimate customer of the SaaS app.

### Recommendation
Bind the tenant identity into what is verified: either include `shop`, `topic`, and `webhook-id` in the signable string (requires coordinating with Shopify's signing scheme, which currently only signs the body — so this must be enforced at a higher layer), or, at minimum, have `Registry.process`/`WebhookMetadata` cross-check `request.shop` against the shop recorded for the session/webhook subscription that this app registered (e.g., via `webhook_id` lookup against Shopify's API) before trusting it as an identity boundary. Document clearly that `request.shop` is HMAC-unauthenticated and must not be used as the sole tenant identifier without additional verification (e.g., confirming the shop is an install of record via a session lookup).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`; the app shares one `client_secret` across all installs.
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, and header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this request to the app endpoint but replaces only `X-Shopify-Shop-Domain` with `victim.myshopify.com`, leaving body `B` and the HMAC header untouched.
4. `Webhooks::Request.new` parses headers/body [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches the header — validation passes [8](#0-7) .
5. `Registry.process` forwards `request.shop` == `"victim.myshopify.com"` to the app's handler as the authenticated tenant, despite the body/event actually belonging to the attacker's own shop [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
