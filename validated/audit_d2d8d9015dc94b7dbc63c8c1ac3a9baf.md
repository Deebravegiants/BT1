Based on the analysis, the `Webhooks::Request` class computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields come from HTTP headers that are never included in that signature. This breaks an identity binding: `verified(body) == trusted(shop)`.

### Title
Webhook shop identity spoofing via unsigned `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  which is what `Utils::HmacValidator.validate` checks against the `hmac-sha256` header [2](#0-1) . However, the `shop` value returned to callers is read directly from the `shop-domain` header without being part of the HMAC-covered content [3](#0-2) .

### Finding Description
`Registry.process` validates the HMAC over the request, then forwards `request.shop` unchanged into `WebhookMetadata` passed to the app's handler [4](#0-3) . Since `hmac` is computed as `Digest.hexencode(Base64.decode64(shopify_header("hmac-sha256")))` and verified against `to_signable_string` (the raw body only), the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are all outside the cryptographic binding. An attacker who can present any HTTP request with a body/hmac pair copied from a legitimate webhook for shop A can freely substitute the `shop-domain` header value to shop B (or any arbitrary value), and `HmacValidator.validate` will still return `true` because it only re-derives the HMAC from `@raw_body`. This breaks the equality that should hold: `shop bound by HMAC == shop delivered to handler`. The gem's own tests confirm this design — the `shop` field is asserted purely from the header value with no relation to the signed payload [5](#0-4) .

### Impact Explanation
This is a cross-tenant identity binding failure: host applications rely on the gem to deliver a trustworthy `shop` identity alongside verified webhook payloads (per the gem's own documentation and `WebhookMetadata` contract) [6](#0-5) . Because `shop` is not bound by the signature, an attacker replaying a captured (or self-obtained, e.g. from their own installed test store) valid `body`+`hmac` pair while forging the `shop-domain` header can cause the host app to process/store webhook data under a victim shop's identity, leading to cross-tenant data confusion in any application that uses `data.shop` from this gem as an authoritative tenant key (as the gem's docs recommend: `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [7](#0-6) ).

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and knowledge of one valid `(body, hmac)` pair — obtainable cheaply by an attacker who installs the app on their own dev store and captures Shopify's own legitimate webhook delivery. No `api_secret_key` or credential is needed to forge the header value itself, since the header is never covered by HMAC.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the HMAC-signed content computed by `to_signable_string`, or otherwise cryptographically bind them to the payload before trusting `request.shop` in `Registry.process`. At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must not be used as a tenant-scoping key without independent verification (e.g. cross-checking against a shop domain already known for the resource in the payload).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, receives a legitimate webhook with headers `x-shopify-hmac-sha256: <valid-hmac>` and `x-shopify-shop-domain: attacker.myshopify.com`, body `{}` (or any captured payload).
2. Attacker replays the exact same request to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `@raw_body` [1](#0-0)  — validation still succeeds because the body/hmac pair is unchanged.
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` despite the payload actually originating from/being signed for `attacker.myshopify.com` [8](#0-7) .

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

**File:** test/webhooks/registry_test.rb (L16-31)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
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

**File:** docs/usage/webhooks.md (L19-29)
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
