This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#hmac` and `to_signable_string` bind the HMAC signature to `@raw_body` only, while `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header and is never included in the signed string.This confirms the pattern fully: `Registry.process` validates HMAC only against `to_signable_string` (the raw body), then passes `request.shop` — read verbatim from the unauthenticated `x-shopify-shop-domain` header — straight into `WebhookMetadata` given to the app's handler as the tenant identifier.### Title
Webhook `shop` identity is read from an unauthenticated HTTP header and is never covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, but exposes `shop` (the tenant identifier ultimately handed to the app's handler) from the `x-shopify-shop-domain` HTTP header, a value that is not included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by calling `Utils::HmacValidator.validate(request)` [1](#0-0) , which in turn calls `validate_signature`, computing `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and comparing it to the `hmac` value with `OpenSSL.secure_compare` [2](#0-1) .

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [3](#0-2) , while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload [4](#0-3) . After a successful HMAC check, `Registry.process` passes `request.shop` straight into `WebhookMetadata` given to the app's handler [5](#0-4) , and `WebhookMetadata#shop` is a plain `String` field with no further validation [6](#0-5) .

The identity binding that should hold is:
`hmac == HMAC(secret, raw_body ∥ shop_header)`, i.e. the header claiming which tenant the webhook is for should be part of what the signature attests to. Instead the code effectively enforces only `hmac == HMAC(secret, raw_body)`, leaving `shop` outside the authenticated envelope. This is the same class of defect as the external report's `totalBorrowed -= lostAmt` bug: the value used downstream for tenant/account bookkeeping (`account.principal` there, `shop` here) is decoupled from the value that was actually verified/authenticated (the real loss vs. the lost amount there; the signed bytes vs. the header here).

### Impact Explanation
Any party that can obtain one genuine, validly-signed webhook body for topic X (e.g., an attacker who installs the target app on their own test shop and receives real webhooks, or intercepts/replays a webhook whose body is generic/predictable) can resubmit the exact same raw body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. Because the header is not covered by the signature, `Utils::HmacValidator.validate` still returns `true`, and the app's handler will process the payload under a forged tenant identity (`data.shop`). Any host application that uses `data.shop` from `ShopifyAPI::Webhooks::WebhookHandler#handle` as the authoritative tenant key (the exact pattern the gem's own documentation recommends: `shop_domain: data.shop`) is exposed to cross-tenant data corruption/attribution — e.g., attaching another merchant's order/customer data to the wrong shop, or triggering shop-scoped side effects (queueing jobs, updating records) keyed by a spoofed shop domain. This matches the Critical "cross-tenant access" impact category, since the tenant boundary (`shop`) is broken while the message still passes signature verification.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one raw body/HMAC pair that is valid for the app (trivially obtainable by installing the app on an attacker-controlled development shop and capturing its own genuine webhook), and requires the host app's webhook route to accept arbitrary caller-supplied headers (true for any standard HTTP endpoint that isn't additionally authenticated by mTLS/IP allow-listing to Shopify's infra). No access to `api_secret_key`, access tokens, or any privileged account is required — only the ability to send an HTTP POST with attacker-chosen headers and a body/signature pair the attacker already legitimately owns. This is a realistic, unprivileged-internet-user attack path fully within the gem's own verification logic.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) header values in the signed/verified material, or independently verify that `request.shop` corresponds to a shop that is actually installed/known to the app (e.g., cross-check against stored sessions) before trusting it, rather than exposing it as an unauthenticated pass-through in `WebhookMetadata`.

### Proof of Concept
1. Install the target app (built on this gem) on an attacker-owned development shop `attacker-shop.myshopify.com`; trigger a webhook (e.g., `app/uninstalled` or `shop/redact`) and capture the raw POST body `B` and the legitimate `X-Shopify-Hmac-Sha256` header `H` sent by Shopify — these are valid because Shopify computed `H = HMAC(client_secret, B)` for the app.
2. Replay a POST to the same app's webhook endpoint with the identical body `B` and header `H`, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...,"x-shopify-shop-domain"=>"victim-shop.myshopify.com", "x-shopify-hmac-sha256"=>H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — verification succeeds [7](#0-6) [8](#0-7) .
4. The registered handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, so the host app processes attacker-controlled data under the victim shop's identity [5](#0-4) .

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
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
