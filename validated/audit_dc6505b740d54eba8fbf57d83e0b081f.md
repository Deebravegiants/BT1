### Title
Webhook `shop`/`topic` headers are not covered by the HMAC signature, allowing tenant spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that `Utils::HmacValidator.validate` verifies — only returns the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated HTTP headers and are never part of the signed payload, yet `Webhooks::Registry.process` trusts `request.shop` as the tenant identity when dispatching to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field of the same object [1](#0-0) . For webhooks, `to_signable_string` is defined as simply the raw body: [2](#0-1) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors all come from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are **not part of the signed string** [3](#0-2) .

`Webhooks::Registry.process` validates only the body's HMAC and then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` that is handed to the app's handler: [4](#0-3) 

The binding the gem should enforce is: `shop conveyed to the handler == shop that produced/authorized the signed payload`. Because `shop` is excluded from `to_signable_string`, that equality is never checked — only `hmac(body) == hmac(body)` is checked, independent of which shop header accompanies it.

The library's own documentation reinforces the unsafe usage pattern, explicitly telling integrators to use `data.shop` as the tenant key for downstream processing (e.g., `perform_later(shop_domain: data.shop, ...)`): [5](#0-4) 

### Impact Explanation
Any real (even unprivileged) merchant who has installed the app on their own shop legitimately receives correctly-HMAC-signed webhook deliveries for their own shop. Because the header carrying the shop domain is not covered by the signature, that same attacker can replay the request to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain — the HMAC still validates since it only covers the body. The app's handler, following the gem's documented pattern, will process/store that (attacker-controlled) body under the victim's tenant identity. This is a cross-tenant data-integrity/isolation break as classified under "Critical - cross-tenant access."

### Likelihood Explanation
High: no secrets, tokens, or privileged access are required — only the ability to install the app as an ordinary merchant (to obtain one legitimately signed body/HMAC pair) and the ability to POST an HTTP request with a modified header to the app's public webhook callback URL.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived shop identity to the verified payload before it is handed to `WebhookMetadata`/the app's handler, so that spoofed headers on an otherwise-valid signature are rejected.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and a valid `x-shopify-hmac-sha256` header computed over `B`.
2. Attacker resends this exact request to the app's webhook endpoint, keeping the body `B` and `x-shopify-hmac-sha256` unchanged, but replacing `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` still returns `true` because `to_signable_string` only checks the body [6](#0-5) .
4. `Registry.process` dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop == "victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-controlled order data as if it belonged to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
