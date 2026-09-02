### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the shop identity used to route and process the webhook is read from an unsigned HTTP header. This breaks the intended binding `hmac == HMAC(secret, body ‖ shop)` down to `hmac == HMAC(secret, body)`, so the `shop` value delivered to application handlers is never authenticated.

### Finding Description
`Registry.process` validates a webhook purely via `Utils::HmacValidator.validate(request)`, and that validator in turn calls `verifiable_query.to_signable_string`: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile `Request#shop` is read straight from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header, which is never included in `to_signable_string` and is therefore never covered by the HMAC: [3](#0-2) [4](#0-3) 

`Registry.process` still forwards this unauthenticated `shop` value directly into `WebhookMetadata`, which is passed to the application's handler and, per the gem's own documented usage pattern, used as the tenant key for downstream persistence/enqueueing: [1](#0-0) [5](#0-4) 

`HmacValidator.validate` confirms only that `hmac == HMAC(secret, to_signable_string)`, i.e. only the body is checked; `secret` (`Context.api_secret_key`) is a single app-wide secret shared across every installed shop, not a per-shop secret: [6](#0-5) 

This is exactly the report's bug class: a field that is acted upon (the `shop` identity used to attribute/route the webhook) is not covered by the same authentication check (the HMAC) that is otherwise relied upon to prove authenticity of the request. Because the API secret is shared by all shops of an app installation, an attacker who legitimately controls one installed shop can obtain a validly-signed webhook (signed with the app's shared secret over that shop's own body) and resubmit it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. The HMAC check still passes (it only checks the body), and the application will process/store the (attacker-supplied) webhook body under the victim shop's identity.

### Impact Explanation
This allows cross-tenant confusion/injection: an attacker-controlled webhook body can be attributed to any other shop that has installed the same app, since the app only trusts `data.shop` after HMAC validation of the body succeeds, and the shop value is not bound to the signature. Depending on how the host application uses `data.shop` (e.g., looking up the shop's session/store record and applying `data.body` to it, as shown in the gem's own documented example), this can result in cross-tenant data corruption/injection attributed to a victim merchant. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Any merchant that installs the target app can generate arbitrary, validly-HMAC-signed webhook traffic for their own store (e.g., by editing their own store's resources to trigger e.g. `products/update`, `orders/create`, etc.), capture the raw body and its valid HMAC, and replay it against the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a different shop. No secrets, tokens, or privileged access are required beyond having their own shop install the app — a normal, unprivileged capability for any Shopify merchant/app user.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signable content verified against the HMAC, or otherwise cryptographically bind the `shop` header to the signed payload before trusting it in `WebhookMetadata`. At minimum, `ShopifyAPI::Webhooks::Request#to_signable_string` should not be limited to the raw body alone if `shop` (and other headers used downstream) are treated as authenticated data by consumers of `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook (e.g., updates a product) and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header Shopify computed with the app's shared `api_secret_key`.
3. Attacker resubmits the exact same body/HMAC to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only recomputes HMAC over `@raw_body` (`lib/shopify_api/webhooks/request.rb`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) builds `WebhookMetadata` using `request.shop`, which is `"victim-shop.myshopify.com"`, and invokes the app's handler as if the (attacker-controlled) body genuinely originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
