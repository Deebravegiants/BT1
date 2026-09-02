### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable HMAC over the raw request body only, while the `shop` (tenant) identifier used by the handler comes from an unauthenticated HTTP header. Because Shopify apps share a single `api_secret_key` across all installations/shops, any merchant who has the app installed can produce a body+HMAC pair that is valid for the app's secret, then replay that exact body/HMAC pair against the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to name a victim shop. `Utils::HmacValidator` only verifies that the HMAC matches the body — it never binds the HMAC to the shop the request claims to be from — so the forged request passes validation and the handler is invoked with an attacker-chosen body attributed to the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from an HTTP header with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` (and `validate_signature`) verify the HMAC strictly against `to_signable_string` (i.e., the body) and the shared `api_secret_key`; it never considers `shop`: [3](#0-2) 

`Webhooks::Registry.process` performs exactly this check and then hands `request.shop` straight to the handler as the trusted tenant identifier, alongside the (also HMAC-verified) body: [4](#0-3) 

The broken identity equality is:
`shop authenticated by the HMAC (∅, none) != shop acted upon by the handler (WebhookMetadata#shop, taken from an unauthenticated header)`

Since the same `api_secret_key` is used for every shop that has the app installed, any unprivileged merchant who installs the app can trigger a real webhook for their own shop, capture the genuine `(raw_body, hmac)` pair Shopify sends them, and replay it verbatim to the app's public webhook endpoint with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header pointing at any other shop. `HmacValidator.validate` will report the signature valid (it never checked the shop), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain while `body` is attacker-controlled (to the extent the attacker can shape their own shop's webhook payload, e.g. order/customer/cart fields they created themselves).

### Impact Explanation
Apps commonly use the webhook's `shop` to look up per-tenant sessions/config and then act on `body` as authentic data for that tenant (e.g., updating orders, inventory, or customer records, or triggering side effects keyed by shop). This gem, by not binding `shop` to the same HMAC that authenticates `body`, hands the host app a spoofable tenant identifier alongside genuinely-signed-but-attacker-controlled content, enabling cross-tenant data injection/access — a High/Critical class of impact per the tenant-isolation boundary the HMAC is meant to enforce.

### Likelihood Explanation
Any actor who can install the app on a shop they control (an unprivileged internet user, since app installation on one's own store requires no special privilege) can obtain valid `(body, hmac)` pairs for the shared secret at will and replay them with a forged shop header to the app's public endpoint. No access token, `api_secret_key`, or privileged account is required — only the ability to receive a webhook for one's own shop and issue an HTTP request.

### Recommendation
Bind the claimed `shop` (and other Shopify-provided identity headers such as `topic`/`webhook-id`, if used for authorization decisions) into the signed material verified by `HmacValidator`, or otherwise have `Webhooks::Registry.process` cross-check the incoming `shop` header against an independently trusted source (e.g., the session/shop the webhook subscription was registered for) before invoking the handler, rather than trusting the header verbatim once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) they control the content of.
2. Attacker captures the genuine request: raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`, per `HmacValidator.compute_signature`/`validate_signature`). [5](#0-4) 
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`. [6](#0-5) 
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...)` and processes attacker-controlled data as if it originated from `victim.myshopify.com`. [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
