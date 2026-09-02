### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) Headers Are Not Covered by the HMAC Verification, Allowing Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, while the shop identity, topic, API version, and webhook id are all read from unauthenticated HTTP headers. The binding the gem should enforce — `shop header == shop that produced this HMAC-signed body` — is never checked, so any caller who can produce one valid `(body, HMAC)` pair for the configured `api_secret_key` can pair that body with an arbitrary `x-shopify-shop-domain` header value and have the app process it as belonging to any shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and the `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from the (attacker-suppliable) HTTP headers with no cryptographic tie to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` uses this validation result to gate the whole request, then immediately forwards the unauthenticated `request.shop` (along with `topic`, `api_version`, `webhook_id`) straight into the handler: [4](#0-3) 

The identity binding that should hold is: `shop bound to the HMAC-verified body == shop delivered to the handler`. In this implementation that equality is never enforced — the HMAC only proves "this body was produced with knowledge of `api_secret_key`"; it says nothing about which shop the header claims to be. The gem's own documentation instructs developers to trust `data.shop` directly for tenant-scoped work (e.g. enqueuing per-shop jobs), reinforcing that this is the gem's intended contract, not a host-application misuse: [5](#0-4) 

### Impact Explanation
Because `shop` is not bound to the signed body, an attacker who can obtain even one legitimate `(raw_body, hmac)` pair for the app's `api_secret_key` — for example by installing the (often public) app on their own store and capturing one of their own webhook deliveries — can replay that exact body/HMAC to the app's webhook endpoint while swapping only the `x-shopify-shop-domain` header to a victim shop's domain. `Registry.process` will still pass HMAC validation (the body is byte-for-byte identical) and will hand the handler a `WebhookMetadata` claiming the victim shop, even though the payload actually originated from the attacker's own store. Any handler logic that uses `data.shop` to select which tenant's records to create/update/delete (a common and gem-recommended pattern) can be tricked into applying attacker-controlled data under another merchant's identity — a cross-tenant data integrity violation.

### Likelihood Explanation
Exploitation requires the attacker to obtain one valid signed webhook body for the target app (trivial if the app is a public/dev-store-installable app, since the attacker can install it on their own shop and trigger a webhook), then replay it to the app's public webhook endpoint with a forged shop header — an unprivileged internet action requiring no possession of the `api_secret_key` itself. This is a realistic, low-effort attack path.

### Recommendation
Bind the shop (and ideally topic/api_version/webhook_id) into the signed material, e.g. include the shop header value in `to_signable_string`, or independently verify that the shop claimed in the header matches a shop for which the app currently holds a valid session/installation record before invoking the handler. At minimum, document prominently that `data.shop` is unauthenticated and must be cross-checked by the host application against known installed shops before being trusted for tenant-scoped operations.

### Proof of Concept
1. Install the target public app on attacker-controlled dev store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and its `x-shopify-hmac-sha256` header `H` (both are freely observable by the attacker since it's their own store and their own webhook endpoint receiving the callback, or they can stand up a receiving endpoint under their control).
2. Send a new HTTP

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
