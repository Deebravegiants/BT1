I have enough evidence to confirm this finding. The `Webhooks::Request` HMAC only covers the raw body, while the `shop` (and `topic`/`webhook_id`) headers are passed unauthenticated to the handler and documented as the tenant identifier.### Title
Webhook shop/topic/webhook_id headers are not covered by the HMAC signature, allowing tenant-identity spoofing via replay of a valid Shopify webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the request using only this body-based HMAC, then forwards the header-derived `shop` value to the app's handler as the trusted tenant identifier [1](#0-0) . This breaks the intended binding: `hmac == HMAC(secret, body)` should imply `shop == the shop that Shopify generated this exact webhook for`, but the gem never binds `shop` (or `topic`/`webhook_id`) into the signed material.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header using `OpenSSL.secure_compare` [3](#0-2) . Since `to_signable_string` is only the body, the HMAC check never covers `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers, which are all read directly off the (attacker-controllable) HTTP headers in `Request#shop`, `#topic`, `#webhook_id`, `#api_version` [4](#0-3) .

`Registry.process` only calls `Utils::HmacValidator.validate(request)` and then immediately builds `WebhookMetadata` from `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` and passes it to the developer-supplied handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
``` [1](#0-0) 

The gem's own documentation instructs app developers to treat `data.shop` as the authoritative tenant identifier for routing/storage decisions (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) , and `WebhookMetadata#shop` is a plain, unauthenticated `String` field [6](#0-5) .

This is directly analogous to the external report's root cause: a value that is *acted on* (here, tenant identity `shop`) is not covered by the same integrity check that gates processing (here, the body-only HMAC), exactly as the external finding shows a "consumed" state that wasn't tied to the same event that triggers minting.

**Broken equality**: the gem implicitly assumes
`HMAC_valid(body) == (shop_header, topic_header, webhook_id_header are authentic for this body)`
but only the body side of that equality is ever checked.

### Impact Explanation
An attacker who obtains any single genuine Shopify webhook delivery (its raw body + valid HMAC) — for example, from their own store, from a shared/publicly logged webhook payload, or by intercepting a webhook meant for another tenant of a multi-tenant app that shares one shared `client_secret`/webhook endpoint — can replay that exact `raw_body`+`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header to name a *different* victim shop. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over the unchanged body. The app's handler then processes/stores this payload under the attacker-chosen `shop`, causing cross-tenant data injection into the wrong tenant's records (e.g., orders, customer data, redact requests) — a cross-tenant boundary violation, which the rules classify as Critical impact.

### Likelihood Explanation
This requires the attacker to already possess one legitimately-signed webhook body+HMAC pair (e.g., from their own shop, which any merchant/installer of the app can trivially obtain by installing the app and triggering a webhook event on their own store) and to be able to POST to the app's public webhook endpoint with custom headers, which is standard unauthenticated internet access to a publicly reachable webhook callback URL. No access to `api_secret_key`, tokens, or privileged accounts is needed — only crafting an HTTP request with a header swapped, which any unprivileged internet user with an account (any Shopify merchant) can do. This matches the "unprivileged-internet-user" threat model in scope.

### Recommendation
Bind the tenant/routing metadata into the signed material or otherwise cryptographically verify it before use:
- Include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified (`to_signable_string`), not just the raw body, so any header substitution invalidates the HMAC; or
- Independently corroborate `shop` against a value obtained through an authenticated channel (e.g., cross-check against the shop associated with the webhook subscription that was registered via GraphQL, keyed by `webhook_id`) before trusting it for tenant routing; or
- At minimum, document loudly that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are NOT covered by the HMAC and must not be trusted for authorization/tenant-isolation decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers an `orders/create` webhook, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — both valid because Shopify itself signed them with the shared `client_secret`.
2. Attacker replays the exact same request to the app's webhook endpoint, but changes the `x-shopify-shop-domain` header to `victim.myshopify.com` (leaving `x-shopify-hmac-sha256` and the raw body untouched).
3. `Registry.process` invokes `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unchanged — and matches the header, so validation passes [7](#0-6) [8](#0-7) .
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` even though the payload originated from and was signed for `attacker.myshopify.com`, and is passed to the app's handler [9](#0-8) .
5. The app's handler, following the gem's documented usage pattern, stores/acts on this data as belonging to `victim.myshopify.com` [10](#0-9) , completing the cross-tenant data injection.

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

**File:** docs/usage/webhooks.md (L10-29)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
