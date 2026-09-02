This confirms the finding: the webhook `hmac` signature is computed only over the raw body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers via `shopify_header`, and are never included in the signed content.### Title
Webhook shop-domain (tenant identity) header not covered by HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator.validate` covers exclusively `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from unauthenticated HTTP headers (`shopify_header`) and are never part of the signed content, yet `Registry.process` uses `request.shop` as the tenant identifier passed to the app's handler.

### Finding Description
The gem's webhook verification binds authenticity to `hmac == HMAC(secret, raw_body)` only: [1](#0-0) [2](#0-1) 

`Registry.process` verifies only this body HMAC, then forwards `request.shop` — taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header — directly into `WebhookMetadata`, which the host application's handler is documented to use as the tenant key (e.g. `data.shop`) for looking up sessions/access tokens: [3](#0-2) [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop header == shop covered by HMAC`. Instead the gem enforces only `hmac(raw_body) == expected`, while `shop` (the field actually acted upon by the handler for tenant routing) is excluded from the signed material. Any party capable of producing one valid `(raw_body, hmac)` pair for the app's secret — e.g., a merchant who has installed the app on their own store and therefore receives genuinely signed webhooks — can replay that exact body+hmac pair while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still return true because it only recomputes/compares against `@raw_body`: [6](#0-5) 

This lets the attacker's own genuinely-signed webhook body be attributed to a victim shop of the attacker's choosing in `WebhookMetadata#shop`, which downstream host code (as documented) uses to select which merchant's session/access token to act on.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the header field (`shop`) that determines which merchant's data/session the handler acts on is not covered by the same integrity check (`hmac`) that authenticates the request. An attacker who legitimately installs the app (a normal, unprivileged action) can obtain valid `(body, hmac)` pairs and then attribute their own webhook content to any other shop domain, causing the app to process attacker-controlled body content under a victim tenant's context. This matches the Critical impact category of cross-tenant access.

### Likelihood Explanation
Likelihood is High for any app that installs the gem's `Webhooks::Registry`/`Request` as documented: the attacker only needs the app installed on their own shop (a normal onboarding step, not a privileged credential) to harvest at least one valid `(raw_body, hmac)` pair, then can freely swap the `shop-domain` header on replay since it's not part of the signed content.

### Recommendation
Include the tenant-identifying headers (at minimum `shop`, and ideally `topic`/`webhook_id`) in the HMAC-signed material, or independently bind the `shop` header to the values embedded in `parsed_body` before trusting it, so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` covers all fields that `WebhookMetadata` exposes to the handler for authorization/tenant-routing decisions.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), receiving from Shopify a request with `raw_body=B` and `x-shopify-hmac-sha256=HMAC(secret,B)`, `x-shopify-shop-domain=attacker.myshopify.com`.
2. Attacker replays this exact request to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed; `HmacValidator.validate` in [7](#0-6)  only checks `HMAC(secret, B)`, which still matches.
4. `Registry.process` succeeds and calls `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...))` as in [3](#0-2) .
5. The host application's handler, per documented usage (`data.shop`), performs actions/lookups against `victim.myshopify.com`'s session using attacker-controlled `body`, achieving cross-tenant effect.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
