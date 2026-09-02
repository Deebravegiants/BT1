### Title
Webhook shop identity (`shop-domain`) is not covered by the HMAC, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator` binds nothing but the payload bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — including the tenant identifier that `Registry.process` hands to the app's handler — are read straight from unauthenticated HTTP headers and are never part of the signed material.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

`Request#shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic tie to the body: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` that is delivered to the app's handler: [3](#0-2) 

`HmacValidator.validate` only compares the received HMAC against a signature computed from `verifiable_query.to_signable_string`, i.e. the raw body for webhooks: [4](#0-3) 

`WebhookMetadata.shop` is the tenant field that downstream app code uses to scope actions to a merchant: [5](#0-4) 

**Identity binding broken (as an equality):**
`hmac == HMAC(client_secret, request.shop_domain_header)` is what the app implicitly relies on when it trusts `WebhookMetadata#shop`, but the actual guarantee is only `hmac == HMAC(client_secret, raw_body)`. `request.shop` (the field acted on — used to select/scope the merchant tenant) is disjoint from the field covered by the HMAC (the raw body only).

Before the attacker's request: a legitimate webhook for shop A arrives with `raw_body = B`, `shop-domain: A`, and a valid `hmac = HMAC(secret, B)`.
After the attacker's request: the attacker resubmits the exact same `raw_body = B` and `hmac` to the app's webhook endpoint, but with `shop-domain: V` (a victim shop that also has the app installed). `HmacValidator.validate` still succeeds because it only checks `HMAC(secret, B)`, and `Registry.process` builds `WebhookMetadata.new(shop: "V", ...)`, delivering attacker-controlled data attributed to the victim tenant.

### Impact Explanation
This crosses a tenant boundary that lives entirely inside this gem's webhook verification logic: `Request`, `HmacValidator`, and `Registry.process` are responsible for authenticating both the payload and the shop attribution before invoking `WebhookHandler#handle`, and `WebhookMetadata#shop` is the documented, intended way for a host app to determine which merchant the webhook concerns — so relying on it is not "ignoring documented API," it is the API's contract. Because the shop attribution is not authenticated, an attacker who controls a legitimate installation of the app (e.g., their own store) can capture a real `(body, hmac)` pair from a webhook Shopify sent them and replay it against the app's public webhook endpoint with a forged shop-domain header naming a different, victim merchant. The app then processes attacker-controlled webhook content as if it originated from the victim shop, which is cross-tenant access/data confusion — no access token, `api_secret_key`, or privileged account is required by the attacker, only observation of one webhook delivery to their own store.

### Likelihood Explanation
Likelihood is High: any developer/merchant who installs the target app can trivially capture one legitimate webhook (body + HMAC) delivered to their own shop, since webhook payloads are visible to the shop owner receiving them, and then replay it with a modified shop-domain header to the same public endpoint. No secret material, brute force, or timing dependency is needed — only header/body it already possesses being resent.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the material verified by the HMAC comparison path, or otherwise cryptographically bind the shop identity to the payload before constructing `WebhookMetadata`. At minimum, `Registry.process` should cross-check `request.shop` against an independently authenticated source (e.g. a known, previously-stored session/shop record) rather than trusting the header outright, since `to_signable_string` for webhooks currently only covers `@raw_body`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) and capture the raw POST: headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, and raw body `B`.
2. Replay the exact same body `B` and `hmac-sha256: H` to the app's public webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (a real shop with the app installed).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, B)` and matches `H` (unchanged since `B` is unchanged) — see [6](#0-5) .
4. The handler executes with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to act on attacker-supplied data as though it came from `victim.myshopify.com`.

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
