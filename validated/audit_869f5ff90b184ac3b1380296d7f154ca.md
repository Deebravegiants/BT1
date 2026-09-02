### Title
Webhook shop identity spoofing via header not covered by HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header [1](#0-0) , while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates is computed over `to_signable_string`, which returns only the raw request body (`@raw_body`) [2](#0-1) . The `Utils::HmacValidator.validate` call verifies `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature` is `HMAC(secret, to_signable_string)` [3](#0-2) . Because `shop` is never part of the signed content, the equality the gem is actually enforcing is:

`HMAC(app_secret, raw_body) == received_hmac`

not

`HMAC(app_secret, raw_body) == received_hmac AND shop == the tenant that the app_secret was used for`.

`Registry.process` then raises only on invalid HMAC [4](#0-3) , and forwards the unauthenticated `request.shop` value straight into `WebhookMetadata` passed to the app's handler [5](#0-4) . Since the `api_secret_key`/`old_api_secret_key` used for the HMAC is a single per-app secret shared across every shop that has installed the app (it is not per-shop), any legitimate, currently-installed merchant (an unprivileged internet user with respect to other tenants of the same app) can obtain a validly HMAC-signed webhook for their own shop from Shopify, then replay that exact body/HMAC pair to the app's webhook endpoint while altering only the `x-shopify-shop-domain` header to name a different, victim shop. The signature check still passes because the header is outside the signed bytes, so the app's handler receives `data.shop == "victim-shop.myshopify.com"` for content that Shopify never actually sent for that shop.

### Impact Explanation
This breaks the tenant identity binding: `shop` (the value used to key sessions/data per the gem's documented webhook contract) is trusted without being covered by the same cryptographic proof (HMAC) that authenticates the payload. Any app that uses `WebhookMetadata#shop` to look up per-shop credentials, apply per-shop business logic, or write per-shop state can be made to act on behalf of, or inject data attributed to, a shop the attacker does not own — i.e., cross-tenant access, which is explicitly listed as a Critical-severity outcome in this analysis's rules.

### Likelihood Explanation
Exploitation only requires the attacker to be a real, currently-installed merchant of the target app (no leaked secrets, no privileged access, no TLS interception) — they legitimately receive valid HMAC-signed webhooks for their own shop and can freely modify the `X-Shopify-Shop-Domain` header of a replayed HTTP POST to the app's public webhook endpoint. This is a low-effort, purely network-level manipulation of an unauthenticated header, making the likelihood high for any app relying on `request.shop`/`WebhookMetadata#shop` for authorization or data attribution.

### Recommendation
Bind the shop identity into the verified material, e.g., include `shop`, `topic`, and `webhook_id` in the signed content used for HMAC validation, or independently verify that `request.shop` corresponds to a shop with an active session/installation known to the app before trusting it, rather than accepting the header value outright once only the body's HMAC passes.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the target app installed.
# Shopify legitimately sends a webhook to the attacker for their own shop:
#   POST /webhooks
#   x-shopify-topic: orders/create
#   x-shopify-hmac-sha256: <valid HMAC of body, computed with the app's shared secret>
#   x-shopify-shop-domain: attacker-shop.myshopify.com
#   body: {"id": 1, ...}
#
# The attacker replays the identical request, only changing the shop header:
raw_body = '{"id": 1, "...": "..."}'
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac,      # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) still succeeds because it only checks HMAC(secret, raw_body).
# The registered handler receives WebhookMetadata with shop == "victim-shop.myshopify.com",
# even though Shopify never issued this webhook for that shop.
``` [4](#0-3) [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
