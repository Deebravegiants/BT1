## Finding: Webhook `shop` identity is not covered by the HMAC signature

The bug-class hint (misleading comments) doesn't map cleanly, but investigating the described analog class — "a field acted on but not covered by the HMAC" — surfaces a real identity-binding gap in the webhook processing path.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is trusted from unauthenticated headers while only the raw body is HMAC-verified — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers without ever being part of the HMAC-signed material [2](#0-1) . `Registry.process` validates only that the body's HMAC matches, then unconditionally trusts `request.shop` and hands it to the app's handler as the tenant identifier [3](#0-2) .

### Finding Description
The equality this breaks is: **`shop` authenticated by the HMAC == `shop` delivered to the handler as the tenant key**. In `HmacValidator.validate`, the signature check covers only `verifiable_query.to_signable_string`, which for webhooks is the raw JSON body [4](#0-3) . The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never part of that signed string, yet `Registry.process` passes `request.shop` straight into `WebhookMetadata` as the shop-of-record for the event [5](#0-4) . Documentation confirms host apps are expected to key their downstream logic off `data.shop` as the trusted tenant identifier [6](#0-5) .

Because HMAC-SHA256 covers only bytes of the body, any party who can obtain one legitimately-signed webhook (e.g., by installing the app — even a free/public listing — on their own store and receiving a real webhook from Shopify) possesses a `(body, hmac)` pair that is valid for that exact body under the shared `api_secret_key`. That party can then replay the identical body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header value. `HmacValidator.validate` will still return `true` because it only checks the body against the signature; `Registry.process` will dispatch the handler with the attacker-chosen `shop` value attached to data that Shopify never actually sent for that shop.

### Impact Explanation
This crosses a tenant boundary: an app that persists or acts on webhook payloads keyed by `data.shop` (exactly as this gem's own documentation recommends) can be made to attribute attacker-supplied event data to a victim shop it has no relationship to, or vice versa — attribute a victim's real event data (if intercepted) to the attacker's own shop scope, or simply desynchronize per-tenant state using a forged shop label. This matches the "cross-tenant access" class of Critical impact defined in scope, since the identity that gates per-tenant data handling is derived from unauthenticated bytes.

### Likelihood Explanation
Any entity capable of installing the app on a shop they control (a normal, unprivileged action for public apps) can obtain a validly-signed webhook body/HMAC pair, then freely forge the `shop-domain` (and other metadata) headers on a replayed POST to the app's public webhook endpoint. No access token, `client_secret`, or privileged credential is required — only the ability to trigger one real webhook delivery to themselves and then re-POST it with modified headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the HMAC-signed material (or otherwise cryptographically bind them to the body), or at minimum have `Registry.process`/`Request` cross-check the `shop-domain` header against an app-provided allow-list/session lookup before constructing `WebhookMetadata`, so the header-derived `shop` cannot diverge from the entity whose secret actually produced the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256: H` header Shopify sent.
2. Attacker POSTs the same body `B` with header `H` to the app's public webhook route, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...forged shop...})` builds successfully [7](#0-6) .
4. `Utils::HmacValidator.validate(request)` succeeds because it only re-hashes `B` against the shared secret [8](#0-7) .
5. `Registry.process` calls the app's handler with `data.shop == "victim.myshopify.com"` even though Shopify never sent this event for that shop [5](#0-4) .

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
