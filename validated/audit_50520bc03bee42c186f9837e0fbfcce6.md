### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook confusion - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields that `Registry.process` hands to the app's webhook handler are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves the body bytes were signed with the app's secret — it proves nothing about which shop (tenant) the body belongs to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from the `shopify-*`/`x-shopify-*` HTTP headers, none of which are part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (i.e. the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates on this HMAC check, then builds `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, and dispatches it straight to the app's handler: [4](#0-3) 

The documented contract explicitly tells integrators that `data.shop` is a trustworthy tenant identifier they should use to route/attribute the webhook body: [5](#0-4) 

This breaks the intended binding `hmac == f(body, shop, topic)`; the gem only enforces `hmac == f(body)`. An unprivileged internet user who is a legitimate (even free/trial) merchant of the app can receive a validly-signed webhook for their **own** shop (any topic they can trigger, e.g. `app/uninstalled`, `orders/create` on their own store), capture the raw body + `X-Shopify-Hmac-Sha256` header, then replay that exact body+hmac pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and optionally `X-Shopify-Webhook-Id`/`X-Shopify-Topic` if the topic-specific body still fits a topic they control) to a **victim shop's** domain. `Utils::HmacValidator.validate` still returns `true` because it only checks the body bytes, so `Registry.process` will invoke the handler with `data.shop` set to the victim's domain while `data.body` is the attacker's own data. Any app whose handler uses `data.shop` to key writes/reads (e.g., "update shop X's cached order state using this body," or "mark shop X's install status") will now act on attacker-supplied content under the identity of a shop the attacker doesn't control — a cross-tenant confusion driven purely by an unauthenticated header value.

### Impact Explanation
This crosses the tenant boundary the gem is trusted to enforce: the webhook processing pipeline is the mechanism by which the library asserts "this body genuinely originates from shop S." Because `shop` isn't part of the signed material, that assertion is false — any caller can attach a validly-signed payload to an arbitrary shop identity. Depending on how the host app's handler uses `data.shop` (which the library's own docs instruct developers to trust and use for routing/business logic), this enables cross-tenant data corruption or disclosure, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-high. No secrets, tokens, or privileged access are required — only the ability to be (or briefly become) a merchant/install of the target app on any shop, which is the normal, unprivileged way to obtain one legitimately-signed webhook body+hmac pair. HTTP headers are trivially forged by any client making a raw POST to the app's public webhook route, since nothing in this gem re-validates them against the signed body.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content used for HMAC verification (or otherwise cryptographically bind them to the raw body before it reaches `HmacValidator`), so any header tampering invalidates the signature. At minimum, document loudly that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC and must not be trusted for tenant attribution without an independent authenticated lookup (e.g., verifying the shop against a known, previously-installed session store) before acting on the webhook.

### Proof of Concept
1. As a legitimate but unprivileged merchant, install the target app on `attacker-shop.myshopify.com` and trigger a webhook topic the app subscribes to (e.g. `app/uninstalled`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Replay that exact raw body and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (keep `X-Shopify-Topic`/`X-Shopify-Webhook-Id` consistent with a topic the app registered).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC from the (unchanged) raw body and matches it against the (unchanged) `hmac` header — validation succeeds.
4. The handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com` but whose `body` is the attacker's own uninstall/order data, causing the app to process attacker-controlled content under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
    end
  end
end
```
```
