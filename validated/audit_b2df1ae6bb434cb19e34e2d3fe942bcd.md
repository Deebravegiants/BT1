### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then trusts the `shop` (and `topic`/`webhook_id`) values taken from unauthenticated HTTP headers to build the `WebhookMetadata` handed to the app's handler. Because the shop identity is never part of the signed content, the binding "HMAC-authenticated request == claimed shop" does not hold, breaking the tenant boundary the gem is meant to enforce.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from caller-supplied HTTP headers, none of which feed into the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only ever hashes `verifiable_query.to_signable_string` (i.e. the body) against the app's `api_secret_key`: [3](#0-2) 

`Registry.process` gates on that HMAC check and then immediately trusts `request.shop` (header-derived) to construct the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is documented as "The shop domain of the webhook" and is the field app developers are expected to use to attribute the webhook to a tenant (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) [6](#0-5) 

The identity-binding equality the gem should enforce is:
`shop value HMAC-authenticated by Shopify == shop value delivered to the app's handler`

Because `to_signable_string` excludes the `shop-domain` header, the actual equality enforced is only:
`raw_body bytes signed by Shopify's HMAC == raw_body bytes received`

An app's `api_secret_key` (client secret) is shared across every shop that has installed the app — it is not shop-specific. Consequently, a valid HMAC computed for a webhook body delivered for Shop A remains valid when replayed with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to Shop B, since the signature check never inspects that header. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` even though the body/content actually originated from Shop A.

### Impact Explanation
This breaks the tenant boundary (cross-tenant confusion): a party who can observe/replay a legitimately-signed webhook body for one shop (e.g., their own store, which they fully control and to which the app is installed) can cause the host application to process that payload under an arbitrary target shop identity, since the HMAC gate provides no binding between body and shop. Any host app logic that uses `WebhookMetadata#shop` to route data into per-tenant storage, invalidate caches, or trigger tenant-scoped actions can be manipulated into acting on/against a different tenant's record using data validated only by the attacker's own signed payload. This matches the "cross-tenant access" class of Critical impact.

### Likelihood Explanation
Requires the attacker to have their own app installation (or any means to capture a validly-signed webhook payload for their own shop) and the ability to POST an HTTP request with attacker-controlled headers to the app's registered webhook endpoint — both are unprivileged, attacker-controlled actions once an app supports webhook processing via this gem, since `Registry.process`/`Webhooks::Request` place no cost or restriction on header values beyond their mere presence.

### Recommendation
Include the `shop-domain` header (and ideally `topic`/`webhook_id`) inside the HMAC-signed payload/comparison, or independently verify that `request.shop` corresponds to a shop that is expected to have generated exactly this signed body (e.g., look up the per-shop context before trusting `WebhookMetadata#shop`, or document explicitly that consumers must not treat `data.shop` as authenticated by the HMAC check alone).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S`) and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker (who controls their own outbound network / can intercept their own webhook delivery) resends the exact same body `B` and HMAC header `H` to the same endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the signature only over `@raw_body` (line 36-38 of `request.rb`) — identical to step 2 — so validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop: "victim.myshopify.com"` (registry.rb line 198) and invokes the app's handler, which now processes attacker-controlled body content attributed to the victim shop.

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
