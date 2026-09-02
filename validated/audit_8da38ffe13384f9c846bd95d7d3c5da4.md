### Title
Webhook shop/topic/webhook-id headers trusted for tenant identity without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so the HMAC verified by `ShopifyAPI::Webhooks::Registry.process` never covers the `shop`, `topic`, `webhook_id`, or `api_version` headers, even though those exact header values are handed straight to the app's webhook handler as trusted tenant/session identifiers.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` method returns only `@raw_body`: [1](#0-0) 
`shop`, `topic`, and `webhook_id` are read directly from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 
`ShopifyAPI::Utils::HmacValidator.validate` verifies the received `hmac` against `HMAC(secret, verifiable_query.to_signable_string)` — i.e., against the body only: [3](#0-2) 
`Registry.process` calls this validator and then, once it passes, forwards `request.shop`, `request.topic`, and `request.webhook_id` unchanged into `WebhookMetadata`, which is passed to the app's handler as the authoritative tenant/topic identity for the event: [4](#0-3) 

This breaks the intended identity binding `shop_authenticated == shop_used_by_handler`: the equality that should hold is "the shop whose secret produced this HMAC" == "the shop the handler treats the event as coming from," but the gem only proves "the secret produced this HMAC for this body" — it proves nothing about which shop header accompanied that body. The library's own documentation confirms `data.shop` is treated as the authoritative shop for downstream processing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this field is acted upon as an identity, not merely informational. [5](#0-4) 

By contrast, the OAuth `AuthQuery` analog in this same codebase does the correct thing: its `to_signable_string` includes `shop` in the signed parameter set, binding the shop value to the HMAC: [6](#0-5) 
This confirms the webhook path is inconsistent with the library's own established pattern of binding identity-carrying fields into the signed payload.

### Impact Explanation
Any unprivileged party who can obtain one legitimately-signed webhook body+HMAC pair for the app (e.g., by installing the app on their own store and triggering a webhook for a subscribed topic) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header for a victim shop. Because the HMAC only covers the body, `HmacValidator.validate` still succeeds, and `Registry.process` will dispatch the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain. Any handler logic that trusts `data.shop` to select which tenant's session/records to update (as the documented best-practice pattern shows) can be tricked into acting on behalf of, or attributing forged data to, a shop the attacker does not control — a cross-tenant identity confusion.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on any shop (including the attacker's own free/dev store) to capture one valid signed webhook body/HMAC pair, and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with modified headers — no access token, `client_secret`, or privileged account is needed. Both preconditions are available to a normal, unprivileged app-installing user.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material used by `to_signable_string`, or otherwise cryptographically bind them (e.g., verify `shop` against Shopify's IP allowlist and/or require it to match an actively-installed session before dispatching to the handler). At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated and must be cross-checked by the host application against known installed shops before being trusted.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g. `orders/create`) to receive a legitimate request with body `B` and header `shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
2. Replay the captured request to the app's webhook endpoint, keeping body `B` and header `shopify-hmac-sha256: H` unchanged, but setting `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` returns `H`; `HmacValidator.validate` recomputes `HMAC(secret, B)` which still equals `H`, so validation succeeds: [7](#0-6) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.shop == "victim.myshopify.com"` even though the event body and signature originated from the attacker's own shop: [8](#0-7)

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
