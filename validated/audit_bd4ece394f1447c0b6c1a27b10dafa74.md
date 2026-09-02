### Title
Webhook `Request` HMAC verifies only the raw body, not the `shop`, `topic`, `webhook_id` or `api_version` headers, allowing cross-tenant/topic confusion via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the body bytes match the HMAC — it never proves that the accompanying `shop`, `topic`, `webhook_id`, or `api_version` headers are the ones Shopify actually sent for that body [2](#0-1) . `Registry.process` nonetheless trusts `request.shop` and `request.topic` unconditionally to route the payload and identify the tenant [3](#0-2) .

### Finding Description
`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic binding to the request [4](#0-3) . The only integrity check performed is `HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string`, i.e., the raw body only [5](#0-4) .

The equality the gem implicitly assumes is:
`HMAC-verified(raw_body) == true` ⇒ `(shop, topic, webhook_id, api_version headers are authentic for this body)`

That equality does not hold, because the signable string never incorporates those header values [1](#0-0) . This is the same identity-binding gap as the reported bug class: a field the application acts on (`shop`, used to key/attribute tenant data) is not covered by the same authenticity check (`HMAC`) that gates processing.

`Registry.process` uses `request.shop` and `request.topic` verbatim to build `WebhookMetadata` and dispatch to the registered handler, with no secondary verification that they correspond to the signed body [3](#0-2) . The documented usage pattern explicitly has host apps key business logic — including job attribution/log lines — off `data.shop` and `data.topic` straight from this unauthenticated metadata [6](#0-5) .

### Impact Explanation
An attacker who is able to obtain any one legitimate `(raw_body, hmac)` pair for the app (e.g., from their own shop that has installed the app, or a leaked/replayed capture) can resend that exact byte-identical body with the same valid HMAC, but with the `shopify-shop-domain` and/or `shopify-topic` headers swapped to arbitrary values, to the app's public webhook endpoint. Because those headers are not part of the signed content, `HmacValidator.validate` still returns `true`, and `Registry.process` will dispatch the handler believing the payload originated from a different shop/topic than it actually did. Depending on how the host app persists webhook data (most integrations key storage/updates by `data.shop`, per the gem's own documented pattern), this enables cross-tenant data confusion/corruption — an attacker-controlled shop's webhook payload can be attributed to and processed under a victim shop's identity.

### Likelihood Explanation
The webhook endpoint is a public, unauthenticated HTTP route by design (Shopify calls it directly), so any internet-reachable attacker can send requests to it. The attacker does not need `api_secret_key` — they only need one authentic `(body, hmac)` sample, which is trivially obtainable by installing the target app on an attacker-controlled development/test shop and capturing its own legitimate webhook deliveries. No privileged credentials are required to mount the header-relabeling replay.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the HMAC-verified signable content (or otherwise cryptographically authenticate them, e.g., by validating the sender's `shop` against an independently known/registered shop domain before trusting the header), so that `to_signable_string` in `lib/shopify_api/webhooks/request.rb` covers the full set of fields that `Registry.process` and downstream handlers act upon, not just the raw body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers a webhook, e.g. `orders/create`.
2. Shopify sends a legitimate webhook request to the app's callback URL with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: orders/create`, a valid `shopify-hmac-sha256` computed over the raw body, and some `raw_body`.
3. Attacker captures this exact `(raw_body, shopify-hmac-sha256)` pair.
4. Attacker resends the same `raw_body` and `shopify-hmac-sha256` to the same endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the HMAC only covers `raw_body` [1](#0-0) .
6. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's data>, ...)` [7](#0-6) , causing the host application to process attacker-controlled data as though it belongs to `victim.myshopify.com`.

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
