### Title
Webhook shop-domain header not covered by HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the body) against `Context.api_secret_key` [3](#0-2) . `Registry.process` accepts the request once this body-only HMAC check passes and hands the unauthenticated `shop` header straight to the app's handler as the tenant identifier [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header used by handler == shop that the HMAC actually authenticates`. Because `to_signable_string` for `Webhooks::Request` only serializes `@raw_body` [1](#0-0) , the HMAC only proves "this body was produced by someone holding `api_secret_key`" — it proves nothing about which shop/topic/webhook_id the payload was intended for. Since a single app's `api_secret_key` is shared across every merchant install, any unprivileged user who installs the app on their own store (or otherwise obtains one legitimately signed webhook body+HMAC pair from Shopify) can replay that exact `raw_body`/`hmac-sha256` pair while swapping the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header to name a different, victim shop. `HmacValidator.validate` still succeeds because it recomputes the HMAC over the same `raw_body` with the same shared secret [5](#0-4) , and `Registry.process` forwards the forged `shop` value from `request.shop` directly into `WebhookMetadata` without any additional cross-check [6](#0-5) , `lib/shopify_api/webhooks/webhook_handler.rb` start=6 end=12.

This is the same bug class as the report: the check validates "the parts that are cryptographically bound" but omits binding a field (`shop`) that the downstream logic treats as authoritative for tenant identity — exactly analogous to checking `sum <= 100` while never validating `share > 0`: a necessary constraint (binding `shop` into the signed payload) is simply absent.

### Impact Explanation
Host applications are documented to use `data.shop` from `WebhookMetadata` as the tenant key (e.g. to look up the merchant's session/access token, or to attribute the webhook body to a specific store) [7](#0-6) . An attacker who controls one shop that has the app installed can trigger a legitimate webhook (their own body+HMAC), then replay/spoof requests to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` naming a victim merchant. The gem's own signature check offers no protection against this because the shop field is never part of the signed material. This crosses a tenant boundary: cross-tenant data confusion/injection into another merchant's webhook processing pipeline, which matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Likely, given: (1) any developer/attacker can become an unprivileged merchant by installing the target app on their own store — no privileged credentials needed; (2) the vulnerable HMAC check is entirely internal to this gem (`Webhooks::Request`/`HmacValidator`/`Registry.process`), so it is reachable purely by calling this gem's documented webhook-processing API as intended, not by the host app deviating from documented usage.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the body) in `Webhooks::Request#to_signable_string`, or otherwise separately verify that the `shop` header matches a shop the app has an active installation/session for before forwarding it to the handler. At minimum, treat `request.shop` as untrusted until cross-checked against known shop sessions before using it as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed webhook topic (e.g. `orders/create`) on their own store, capturing the raw request body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify computed with the app's shared `api_secret_key`.
3. Attacker sends a forged HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses this into a `Request` object; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation passes [3](#0-2) .
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the app to process attacker-controlled webhook content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
