Confirmed: the webhook `shop` identity is derived purely from an unauthenticated header, while the HMAC only covers the raw body.

### Title
Webhook `shop-domain` header is trusted as tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then uses the unauthenticated `shop-domain` header as the tenant identity handed to the app's handler. Because the app's `client_secret` (`Context.api_secret_key`) is shared across every shop that has installed the app, any merchant who has installed the app can legitimately obtain a body+HMAC pair for their own shop and then replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header. The HMAC check passes (it never covers the header), and the handler is invoked believing the body originated from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relationship to the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which signs/verifies `to_signable_string`, i.e. the body only), and then immediately trusts `request.shop` as the tenant identity passed into the registered handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute `HMAC(secret, to_signable_string)` and compare against the header-derived signature — again, only the body is part of the signable string: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop delivered to the handler as tenant context`. Because the HMAC secret (`api_secret_key`) is per-app, not per-shop, and the signable string excludes the `shop-domain` header, any shop that has installed the app can compute (via Shopify's own legitimate webhook delivery to their own store) a valid `(body, hmac)` pair, and then submit a forged request to the app's public webhook endpoint with that same valid `(body, hmac)` but an attacker-chosen `shop-domain` header naming a different (victim) tenant. `Registry.process` cannot distinguish this from a legitimate webhook for the victim shop, and hands the attacker's data to the handler tagged with the victim's shop domain — a cross-tenant identity confusion at the exact seam the gem is responsible for (request authentication → tenant attribution).

### Impact Explanation
Handlers are documented to key persistence, background jobs and per-tenant business logic directly off `data.shop`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`: [5](#0-4) 

Since this `shop` value is what every downstream consumer of this gem's webhook API is told to trust as the source-of-truth tenant identifier, an attacker-controlled shop can inject arbitrary attacker-chosen data (subject to the JSON body validating against the topic's expected shape) that the app processes and stores as belonging to a victim's shop, i.e. cross-tenant data injection/confusion through the gem's own webhook processing entry point.

### Likelihood Explanation
Any threat actor who can install the target app on their own Shopify store (a normal, unprivileged action available to any merchant) can trigger a real webhook to obtain a valid `(body, hmac)` pair for arbitrary webhook topics they control (e.g. by creating an order, updating a product, etc.), then replay that pair against the app's public webhook endpoint with a different `shop-domain` header value. No access to the app's `client_secret`, any merchant's access token, or any privileged credential is required.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header into the signed material that `HmacValidator` verifies, or otherwise cryptographically bind the header value to the specific shop's registered session/webhook subscription before passing it to the handler, so that the HMAC verifies the same identity that is ultimately trusted by application code.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, obtaining an active OAuth grant (this is unprivileged/normal usage, not a leaked credential).
2. Attacker performs an action that triggers a real webhook (e.g. `orders/create`) to their app's endpoint. Shopify sends: `raw_body = B`, header `x-shopify-hmac-sha256 = H`, header `x-shopify-shop-domain = attacker.myshopify.com`. Because `HmacValidator` only signs `B`, `H = HMAC(client_secret, B)` is valid regardless of the shop header value.
3. Attacker crafts a new HTTP POST to the app's webhook endpoint reusing the exact same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain = victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation succeeds.
5. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` is passed to the app's handler, which processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
