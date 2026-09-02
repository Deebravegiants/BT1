### Title
Webhook shop-tenant field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` value that is handed to the application's handler as the tenant identifier comes from an HTTP header that is never included in the signed bytes. This is the same class of bug as the report: a field that is *acted upon* (used to route/attribute data) is not part of the data actually covered by the cryptographic check, so the two can be made to disagree.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read directly from the unauthenticated `shopify-shop-domain` (or `x-shopify-shop-domain`) header: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, request.to_signable_string)` and only ever checks the raw body bytes: [3](#0-2) [4](#0-3) 

After the HMAC check passes, `request.shop` (the unauthenticated header value) is forwarded, unverified, as the tenant identifier to the application's registered handler via `WebhookMetadata`: [5](#0-4) 

The library's own documentation confirms this is the intended and only integration pattern: developers are told `data.shop` is "The shop domain of the webhook" and are shown examples that key application-level actions (e.g., enqueuing jobs "per shop_domain") directly off this value, with no guidance to cross-check it against a known/installed-shop list: [6](#0-5) 

**Binding broken (equality that should hold but doesn't):**
`shop` bytes verified by the HMAC == `shop` bytes acted on by the handler.
In reality: `shop` bytes verified by HMAC == ∅ (the signable string is body-only), while `shop` bytes acted on = arbitrary header value chosen by whoever sends the HTTP request.

### Impact Explanation
Any unprivileged internet user who can obtain **one** valid `(raw_body, hmac)` pair signed with the app's `client_secret` — which is trivially available to any attacker by installing the target app on their own free/dev Shopify store and triggering a webhook for a topic/body of their choosing — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value naming a victim shop. `HmacValidator.validate` will still succeed (it never looks at the header), and `Registry.process` will invoke the app's handler with `shop` set to the victim's domain and attacker-chosen `body`/`topic` content.

Because handlers are documented and expected to key persistence, redaction, uninstall, and other per-tenant side effects off `data.shop` (as shown in the gem's own docs example, `shop_domain: data.shop`), this allows an attacker to forge webhooks *as if they came from the victim shop* — e.g. spoofing `app/uninstalled`, `shop/redact`, `customers/redact`, or `customers/data_request` payloads attributed to a different merchant, or injecting attacker-controlled order/customer data tagged with a victim's shop domain into the host application's per-tenant data store. This is a cross-tenant integrity/authentication break within the credential boundary the gem is responsible for validating (it explicitly promises `process` "will verify the request did indeed come from Shopify"), even though the `shop` field it hands out is not verified at all.

### Likelihood Explanation
High likelihood: the attacker only needs their own (free) Shopify development store to install the target app and receive a legitimately-signed webhook, giving them a valid signature over body content they fully control (including customer/shop-adjacent field values embedded in the JSON body, and certainly the freedom to choose which topic and payload shape to trigger). No access to `api_secret_key`, tokens, or the victim's credentials is required — the only thing forged is an HTTP header that this gem's signature check never touches.

### Recommendation
- Include the shop domain (and other routing headers such as topic/api-version/webhook-id where relevant) in `to_signable_string`, or otherwise cryptographically bind the header value to the signed payload before exposing it as `request.shop`.
- At minimum, document prominently that `data.shop` is **not** covered by HMAC verification and must be cross-checked by the host application against the set of shops for which the app currently holds a valid access token/session before being used for any tenant-scoped action.
- Consider exposing a `Registry.process` option that requires callers to pass an expected/known shop list or a session lookup callback, failing closed if `request.shop` does not correspond to an installed shop.

### Proof of Concept
1. Attacker installs the victim app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers (or crafts, since only the HMAC over the body matters) a webhook delivery, capturing `raw_body` and the resulting valid `X-Shopify-Hmac-Sha256` value signed with the app's real `client_secret`.
3. Attacker replays this exact request to the app's webhook endpoint, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <topic of their choice, matching the captured body>`
4. Server code:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(
     ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
   )
   ```
   calls `HmacValidator.validate(request)` which only hashes `raw_body` — validation **succeeds**.
5. The registered handler is invoked with `data.shop == "victim-shop.myshopify.com"` and attacker-controlled `data.body`, even though the request has nothing to do with `victim-shop`. [7](#0-6) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
