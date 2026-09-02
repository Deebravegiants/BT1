Confirmed: the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers in `lib/shopify_api/webhooks/request.rb` are read directly from HTTP headers and are never included in `to_signable_string` (only `@raw_body` is signed), yet `Registry.process` trusts `request.shop` as the tenant identity passed to the host app's handler.

### Title
Webhook shop-domain (and topic/webhook-id/api-version) identity fields are unauthenticated by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, via `to_signable_string` returning `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled straight from HTTP headers with no cryptographic binding to that HMAC [2](#0-1) . `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then forwards the header-derived `shop` value straight into `WebhookMetadata` for the app's handler, treating it as the authenticated tenant identity [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac_signed_bytes == bytes_the_app_treats_as_authenticated`. Here it does not: only `raw_body` bytes are covered by `OpenSSL::HMAC.hexdigest(..., secret, to_signable_string)` in `HmacValidator.validate_signature` [4](#0-3) , while `shop`, `topic`, `webhook_id`, and `api_version` are read unauthenticated from headers [2](#0-1) .

Any unprivileged user can install the app on their own (attacker-controlled) development shop and legitimately trigger a webhook delivery — e.g. by creating an order — for a body/topic they fully control. Shopify will send a request with a correct HMAC for that raw body, computed with the app's real `client_secret`. Because the signature covers only the body, the attacker can capture that valid `(raw_body, hmac)` pair and replay it directly to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, `X-Shopify-Api-Version`) with a different, victim shop's domain. `HmacValidator.validate` still returns `true` because it only recomputes the digest over `raw_body` [5](#0-4) . `Registry.process` then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the host app's handler using the forged, unauthenticated `shop` [6](#0-5) .

The gem's own documentation instructs app developers to treat `data.shop` as the tenant key for dispatching per-shop work (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [7](#0-6) , confirming that this field is relied upon as an authenticated tenant identifier by design.

### Impact Explanation
This breaks the "shop authenticated vs. shop used as tenant/session key" binding explicitly called out as in-scope. An attacker can forge webhook deliveries that are accepted as valid (HMAC passes) but are attributed to an arbitrary victim shop domain of the attacker's choosing, while the body content and topic are attacker-controlled inputs from the attacker's own real, HMAC-signed webhook. Depending on the topic chosen (including the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request` which have no other authorization layer, per `MANDATORY_TOPICS` in `lib/shopify_api/webhooks/registry.rb`), this lets the attacker inject fabricated events into another tenant's data pipeline — a cross-tenant confusion/injection that Sherlock-style criteria classify as Critical (cross-tenant access).

### Likelihood Explanation
Exploitation requires only: (1) installing the app on any shop the attacker controls (a normal, unprivileged action any Shopify developer can take), (2) triggering a webhook for a body/topic of the attacker's choosing, (3) capturing that valid HMAC + raw body pair, and (4) replaying it to the public webhook endpoint with a swapped `shop-domain` (and other) headers. No secrets, tokens, or privileged access are required — this is directly reachable by any unprivileged internet user with knowledge of the app's public webhook URL.

### Recommendation
Bind the tenant/topic identity to the HMAC input. Concretely, include `shop`, `topic`, `webhook_id`, and `api_version` header values in `to_signable_string` (Shopify does not sign headers itself, so this must be done as an app-level defense), or — better — have `Registry.process` independently verify that the `shop` a handler receives corresponds to a shop for which the app currently holds a valid session/registration (looking up by webhook registration rather than trusting the header blindly), and reject requests whose header-derived `shop` is not associated with an actual currently-registered webhook subscription for that topic before dispatching to the handler.

### Proof of Concept
1. Register the app on attacker-owned shop `attacker.myshopify.com` and subscribe to `orders/create`.
2. Trigger an order creation; Shopify POSTs a webhook with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, and a valid `X-Shopify-Hmac-Sha256` computed over the raw body with the app's real `client_secret`.
3. Capture the raw body and the valid HMAC header value.
4. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` (it only checks `raw_body`) as shown by `to_signable_string` returning `@raw_body` [1](#0-0) .
6. `Registry.process` calls the registered handler with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"` even though Shopify never actually sent this webhook for that shop [6](#0-5) .

### Citations

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
