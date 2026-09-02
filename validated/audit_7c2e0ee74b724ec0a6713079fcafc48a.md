### Title
Webhook `shop-domain`, `topic`, `webhook-id` and `api-version` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `WebhookHandler` implementations are read from unauthenticated HTTP headers. This breaks the intended binding "HMAC-verified bytes == data acted upon," analogous to the H-19 pattern where one array (`selectors`) is validated while a different, decoupled array (`plugins`) is actually used at execution time.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` — the values that `Registry.process` extracts and hands to the app's registered `WebhookHandler` — come from HTTP headers that are never included in the signed bytes: [3](#0-2) [4](#0-3) 

`WebhookMetadata` (the object handed to the app's business logic) embeds this unauthenticated `shop` value directly: [5](#0-4) 

The identity binding that should hold is: `shop bound by HMAC == shop used to route/act on the webhook`. In this gem it instead holds: `HMAC covers body only`, `shop is taken from an unauthenticated header`. This is precisely the "field acted on but not covered by the HMAC" analog called out in the validation rules.

### Impact Explanation
Because only the raw body is signed, an attacker who possesses a single genuine, validly-signed webhook delivery (e.g., from their own shop where they installed the app, or one leaked/logged/replayed from any tap on the wire before TLS termination at the app) can replay that exact `raw_body` + `hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass, since it only recomputes the HMAC over the untouched body. `Registry.process` will then dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen shop instead of the shop the payload actually originated from. Any host application that trusts `data.shop` from `WebhookHandler#handle` (e.g., to look up which merchant's session/local records to update) can be tricked into applying another tenant's webhook data under a different shop's identity — a cross-tenant integrity/confusion issue reachable by anyone who can capture one legitimately signed webhook body.

### Likelihood Explanation
Exploitation requires capturing at least one legitimately-signed webhook (trivial for anyone who installs the vulnerable app on their own development/test shop, since Shopify sends real signed webhooks to every installed app) and replaying it with a modified `shop-domain` header, which requires no access to `api_secret_key` or any merchant credential. This is a realistic, low-cost attack path fully reachable through the gem's own public API surface (`Webhooks::Request` / `Webhooks::Registry.process`).

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`, and ideally a timestamp) in the HMAC-signable string for webhooks, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signed payload: [6](#0-5) 
At minimum, document and/or enforce that consumers of `WebhookMetadata#shop` must cross-check it against an independently-verified shop association (e.g., an existing session for that shop) rather than trusting the header value implicitly.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery, e.g. `orders/create`, including its raw body and the `x-shopify-hmac-sha256` header — this is a validly-signed payload per `HmacValidator`.
2. Replay this exact `raw_body` and `x-shopify-hmac-sha256` value to the same app endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` computes `compute_signature(request.to_signable_string, secret)` — since `to_signable_string` returns only `@raw_body` (unchanged), the signature check passes: [2](#0-1) 
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now reads `"victim.myshopify.com"` from the forged header: [7](#0-6) 
5. The app processes the attacker's order/customer data as if it belongs to `victim.myshopify.com`, corrupting or cross-contaminating that tenant's data/state.

### Citations

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
