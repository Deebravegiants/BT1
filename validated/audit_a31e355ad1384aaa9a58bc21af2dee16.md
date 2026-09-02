## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying that the HMAC in `x-shopify-hmac-sha256` matches the raw request body [1](#0-0) . However, the tenant-identifying field it then hands to the app's handler — `shop` — is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header and is never part of the signed material [2](#0-1) .

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the value carried in the `hmac-sha256` header: [4](#0-3) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from unauthenticated headers: [5](#0-4) 

`Registry.process` verifies only the HMAC and then dispatches directly to the registered handler using `request.shop`, with no additional binding check between the shop and the signed body: [6](#0-5) 

The identity-binding equality that should hold is: `shop-domain header == shop that produced/authorized this exact body`. Because the HMAC only proves "this body was HMAC'd with the app's secret" and says nothing about which shop that body belongs to, an unprivileged internet user who obtains **any** one valid `(raw_body, hmac)` pair for the app (trivially available by installing the app on their own free/dev store and capturing one of its own genuine webhook deliveries) can replay that exact body with the HMAC unchanged while substituting `x-shopify-shop-domain` (and `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`) for an arbitrary victim shop. `HmacValidator.validate` will still pass, because it never inspects the header values, and `Registry.process` will invoke the handler believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to guarantee: "the shop asserted in the webhook equals the shop that Shopify actually sent it for." Any host application that uses `data.shop` (as explicitly documented) to select which merchant record, session, or access token to act on — e.g., queueing background jobs keyed by shop, updating shop state, or handling the mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics — can be made to perform actions against a shop the attacker doesn't control, using a body the attacker fully chooses (as long as it was legitimately HMAC'd for their own store). This is a cross-tenant confusion vulnerability reachable by any unauthenticated internet user with a free trial store, satisfying the "cross-tenant access" Critical impact bucket.

### Likelihood Explanation
Likelihood is High: creating a Shopify development/trial store and installing any public app that uses this gem is free and requires no special privileges. Capturing one's own webhook body+HMAC and replaying it with forged headers to the app's public webhook endpoint requires no secrets, only observation of one's own genuine webhook traffic.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material that the app trusts, e.g., by requiring host apps to look up an expected shop from their own session store using an out-of-band trusted identifier before dispatching, or by extending `to_signable_string`/`HmacValidator` to incorporate the header values that the handler relies on so that any header tampering invalidates the HMAC check. At minimum, document explicitly and loudly in `docs/usage/webhooks.md` that `data.shop` is unauthenticated and must be cross-checked by the host application against its own session/shop registry before being trusted, since currently the docs present `data.shop` without that caveat [7](#0-6) .

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` (free dev store) and lets it register a webhook, e.g. `orders/create`.
2. Shopify delivers a genuine webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` and replays a new HTTP POST to the same endpoint with the same body `B` and the same header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)`, which still equals `H`, and returns `true` at [8](#0-7) .
5. `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` [9](#0-8) , causing the host application to act on behalf of `victim.myshopify.com` using attacker-chosen body content.

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
