### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted by the handler without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The shop domain (and other metadata) that is subsequently handed to the app's webhook handler is read from an HTTP header that is **not** part of the signed payload, so it can be freely substituted by anyone who possesses one valid `(raw_body, hmac)` pair for the app.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `hmac` is taken straight from the `hmac-sha256` header: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from separate headers that are never mixed into `to_signable_string`: [3](#0-2) 

`HmacValidator.validate` verifies exactly and only `to_signable_string` against `hmac`: [4](#0-3) 

`Registry.process` performs only that HMAC check and then forwards `request.shop` (and the other header-derived fields) verbatim to the host app's handler as trusted metadata: [5](#0-4) 

The documented usage pattern explicitly treats `data.shop` as the authenticated tenant identifier for the event, e.g. used to route/attribute the webhook payload to a specific shop: [6](#0-5) 

**Broken identity binding:** the equality that should hold is `shop authenticated by HMAC == shop delivered to handler`. In reality, HMAC only authenticates `raw_body`; `shop` is an independent, unsigned header. Once an attacker legitimately receives one webhook delivery for a shop they control (e.g., their own development store with the same app installed), they possess a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. They can replay this exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: <attacker-chosen victim shop>, ...)`.

### Impact Explanation
This breaks the tenant/session boundary: the gem hands the host application a spoofed shop identity carried on an otherwise-authentic (HMAC-valid) request. Any host app that uses `data.shop` to attribute, store, or act on webhook data per-tenant (the exact pattern shown in this gem's own documentation) can be made to process fabricated events "from" any shop the attacker chooses, using nothing more than a webhook payload the attacker legitimately received for their own shop. This is a cross-tenant event/data injection primitive — the impact category matches "cross-tenant access" since it lets an unprivileged party attribute arbitrary payload data to another merchant's tenant record without ever possessing that merchant's credentials.

### Likelihood Explanation
Any developer/attacker can install the target app on a shop they control (or use a development store) to receive one legitimately-signed webhook delivery. Replaying it with a modified `shop` header is a trivial HTTP request; no secret material, session, or privileged access is required, and the vulnerable check (`Utils::HmacValidator.validate`, `Webhooks::Registry.process`) is exactly the code path this gem tells integrators to rely on for authentication.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind them to the body before trusting them (e.g., have `to_signable_string` incorporate the shop domain/topic, or require the host app to cross-check `shop` against a known, previously-authenticated session/shop list before acting on the webhook). At minimum, document prominently that `data.shop` and other header-derived `WebhookMetadata` fields are NOT covered by the HMAC and must not be trusted for tenant attribution without additional verification (e.g., matching against the shop associated with the specific `webhook_id`/subscription via a Shopify API lookup).

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and configure a webhook (e.g. `orders/create`).
2. Trigger an event so Shopify delivers a legitimate webhook: capture `raw_body` and the `x-shopify-hmac-sha256` header value.
3. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but set:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb` `to_signable_string`, `lib/shopify_api/utils/hmac_validator.rb`).
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's original payload>, ...)` and the host app processes/stores it as if it genuinely originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** docs/usage/webhooks.md (L12-30)
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
    end
  end
end
```
```
