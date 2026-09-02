The strongest analog here is in the webhook verification path. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC covers exclusively the body bytes, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers and passed straight to the handler.### Title
Webhook HMAC only covers the raw body, not the shop-domain header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies solely `HMAC(secret, raw_body)`. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Webhooks::Registry.process` are read directly from HTTP headers that are excluded from the signed payload. This breaks the intended identity binding `HMAC-verified(payload) == payload attributed to shop`, letting anyone who can produce one valid `(raw_body, hmac)` pair for their own shop replay it while asserting a different, victim shop.

### Finding Description
`HmacValidator.validate` computes and compares `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` against the received HMAC: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body bytes: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are never included in the signed string: [3](#0-2) 

`Registry.process` trusts these unauthenticated fields directly, verifying only the HMAC before dispatching to the app's handler with the header-derived `shop`: [4](#0-3) 

Because a single `api_secret_key` is shared across every shop that installs the app (it is a per-app secret, not per-shop), any merchant who installs the app on their own store legitimately receives real webhooks with valid HMACs computed over their own body. The `shop-domain`, `topic`, and `webhook-id` headers carried alongside that valid `(body, hmac)` pair are not bound by the signature, so they can be freely substituted before delivering the request to the app's webhook endpoint. The equality the code relies on — "HMAC valid ⇒ body legitimately originated for the asserted shop" — does not hold, since the shop identity is asserted via an unsigned header rather than being part of the HMAC-covered payload.

### Impact Explanation
This crosses a tenant boundary: an app receiving webhook processes attacker-controlled body content while attributing it to an arbitrary victim shop (`WebhookMetadata#shop`), since `shop` is taken straight from `request.shop` with no cryptographic tie to the signed body. Depending on the app's webhook handler logic (as documented and expected in `docs/usage/webhooks.md`), this can drive cross-tenant data writes, spoofed lifecycle events (e.g., replaying a legitimate `orders/create`/`app/uninstalled` payload under a different `shop-domain`), or corruption of per-shop state — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any actor who can install the target app on their own Shopify store (a normal, low-privilege action) — no leaked secrets, TLS interception, or social engineering is required. They only need to capture one legitimate webhook body+HMAC pair from their own tenant and can then freely relabel the shop/topic/webhook-id headers when replaying it to the app's public webhook endpoint.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload used for verification (or otherwise cryptographically bind them, e.g., by hashing header+body together and comparing against the signature), rather than trusting them independently of the signature check performed in `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value — this HMAC is valid because it's computed with the app's single shared `api_secret_key` over `raw_body` only.
2. Attacker crafts a new HTTP request to the app's webhook endpoint using the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)`: [5](#0-4) 
4. The registered handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com` even though the body was attacker-authored, breaking tenant isolation.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
