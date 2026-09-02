### Title
Webhook shop identity not bound to HMAC signature enables cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then forwards the header-derived `shop` value, unverified, to the app's handler as the tenant identity. This lets any user who can obtain one genuine `(body, hmac)` pair — e.g., by installing the app on their own store — replay it against the app's webhook endpoint with a forged `shop-domain` header, causing the handler to process attacker-controlled data under a victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers, none of which are included in the signed bytes: [2](#0-1) 

`HmacValidator.validate` verifies `request.hmac` against `to_signable_string` (i.e., raw body only) with the shared `api_secret_key`: [3](#0-2) 

`Registry.process` only calls this body-only HMAC check, then constructs `WebhookMetadata` directly from the unauthenticated `request.shop` header and hands it to the app's handler: [4](#0-3) 

The gem's own documentation instructs host apps to use `data.shop` as the tenant/routing key for further processing (e.g., enqueuing a background job scoped to that shop): [5](#0-4) 

This breaks the equality that should hold: `shop_bound_by_HMAC == shop_used_for_tenant_routing`. In this gem, the HMAC binds nothing about `shop` at all — the signature only proves the body byte-for-byte matches what was signed with the app-wide `api_secret_key`, not which shop it belongs to.

### Impact Explanation
Because Shopify webhook secrets (`api_secret_key`) are shared by the app across all installations, any unprivileged user who installs the app on their own store (a normal, unprivileged action) receives genuine webhook deliveries with valid `(body, hmac)` pairs signed by the same secret used for every other merchant. That user can capture one such delivery and replay it to the app's public webhook callback URL while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because the header isn't part of the signed content, and `Registry.process` passes the forged `shop` straight through to the handler as `WebhookMetadata#shop`. Any host app following the gem's documented pattern (using `data.shop` to route data, look up a shop's queue, or attribute events) will process attacker-supplied data as if it originated from the victim shop — a cross-tenant integrity/isolation break driven entirely by this gem's design of not binding the identity field to the authentication mechanism.

### Likelihood Explanation
High. No access token, `client_secret`, or other privileged credential is required — only one legitimate webhook delivery from the attacker's own store install, which any internet user can obtain by installing the target app. The exploit requires only replaying an HTTP request with a modified header value, since the gem itself performs no binding between the authenticated bytes (body) and the identity value (`shop`) it hands to application code.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the raw body) in the HMAC-covered content, or independently verify that the `shop` header value matches a shop the app has an active registration/session for before dispatching to the handler. At minimum, document prominently that `data.shop` is not authenticated by the HMAC check and must not be trusted as a tenant key without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Install the target Shopify app on `attacker-shop.myshopify.com` (no special privilege needed) and trigger any subscribed webhook topic (e.g., `orders/create`) to receive a legitimate delivery with headers `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and some `raw_body`.
2. Replay this exact HTTP request to the app's webhook callback endpoint, but change only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`, leaving the body and HMAC header untouched.
3. Trace through gem code:
   - `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request object from the (attacker-controlled) headers.
   - `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks `raw_body`, unaffected by the header change.
   - `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and forwarded to `handler.handle(data:)`.
4. The host app's handler (following the gem's documented pattern of using `data.shop` for routing/storage) processes attacker-supplied body content as belonging to `victim-shop.myshopify.com`.

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
