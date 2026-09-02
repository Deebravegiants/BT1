### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, which validates the HMAC over `Webhooks::Request#to_signable_string`. That method returns only `@raw_body`. The `shop` value (from the `X-Shopify-Shop-Domain` header) is read separately via `shopify_header("shop-domain")` and is never part of the signed bytes, yet it is forwarded, trusted, into the app's `WebhookHandler#handle` as the tenant identifier.

### Finding Description
The identity binding that should hold is: `HMAC-verified bytes == bytes the app treats as authoritative` for every field used to route/scope the request, i.e. `signed(raw_body, shop) == (raw_body, shop)` acted upon. In this gem that equality is broken:

- `Webhooks::Request#to_signable_string` (lib/shopify_api/webhooks/request.rb) returns `@raw_body` only. [1](#0-0) 
- `Webhooks::Request#shop` is parsed straight from an HTTP header outside the signed payload. [2](#0-1) 
- `Registry.process` validates only the HMAC and then dispatches directly using `request.shop`, with no cross-check that the header's shop matches the body's actual originating shop. [3](#0-2) 
- `HmacValidator.validate` computes and compares the signature strictly against `verifiable_query.to_signable_string`, i.e. `raw_body` — the shop header plays no role in the cryptographic check. [4](#0-3) 

Because Shopify's own webhook HMAC (per Shopify's webhook spec, which this gem mirrors) is computed over the raw body and the shared `client_secret`/webhook secret — not over headers — a valid `(raw_body, hmac)` pair for shop A remains a valid `(raw_body, hmac)` pair regardless of what `X-Shopify-Shop-Domain` header accompanies it. An attacker who legitimately receives one authentic webhook (e.g. as a merchant/developer running their own store subscribed through the same app) can replay that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` value. `HmacValidator.validate` still returns `true` (the body/HMAC pair is unmodified), and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` to the app's handler with the attacker-chosen `shop` value.

The documented handler contract explicitly tells implementers to trust `data.shop` as the tenant identifier for background processing (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so any app following this gem's documented pattern will attribute shop-A's webhook payload to an attacker-chosen shop. [5](#0-4) [6](#0-5) 

### Impact Explanation
This crosses the tenant boundary that `WebhookMetadata#shop` is meant to guarantee: an attacker controlling only their own store's webhook traffic can cause the app to process a genuine, HMAC-valid event body labeled as belonging to a different, victim shop. Depending on how the host app's handler uses `data.shop` (record scoping, authorization, triggering privileged actions "for" that shop), this enables cross-tenant data confusion/injection using replayed real payloads — matching the "cross-tenant access" impact class, since the field the app relies on to select the tenant is not covered by the cryptographic authentication check.

### Likelihood Explanation
Exploitation requires only an unprivileged internet user who has legitimate access to at least one shop subscribed to the same app (to obtain one valid raw_body+HMAC pair) and the ability to POST to the app's public webhook endpoint with a forged header — no `api_secret_key`, access token, or privileged account is needed. This is a realistic, low-effort attack path fully reachable through this gem's own `Webhooks::Request`/`Registry.process` API as documented.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material, or otherwise cryptographically bind the header value to the verified payload before trusting it. At minimum, `to_signable_string` should not be limited to `@raw_body`; require the host app to re-verify the shop is one it registered a webhook for, or perform an authoritative shop lookup independent of a self-reported header before treating `WebhookMetadata#shop` as the tenant identity.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com`, installed on the target app, and receives a genuine webhook: raw body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and compares to `H` — validation succeeds because `B`/`H` are unmodified. [7](#0-6) 
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the attacker-supplied header value `victim-shop.myshopify.com` and invokes the app's handler with it. [8](#0-7) 
5. The app's handler, following this gem's documented usage pattern, processes/enqueues work "for" `victim-shop.myshopify.com` using data that actually originated from `attacker-shop.myshopify.com` — a cross-tenant identity confusion enabled purely by data the gem itself never authenticates.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
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
