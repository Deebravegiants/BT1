This confirms the vulnerability class: `WebhookMetadata.shop` is documented and used by app developers to key their per-tenant logic (`data.shop`), but that field is derived from an HTTP header that is not part of the HMAC-signed bytes.

### Title
Webhook `shop` field trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` value that `ShopifyAPI::Webhooks::Registry.process` forwards to the app's handler is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed bytes. Because a single app `client_secret` is shared across every shop that installs the app, any shop that can trigger a webhook for itself controls a validly-signed `(body, hmac)` pair that will also validate under any other shop's identity if the shop header is swapped, breaking the intended binding `hmac == HMAC(secret, body_for_shop_X)` implies `shop == X`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `Request#shop` is read directly, unauthenticated, from the request headers: [2](#0-1) 

`Registry.process` validates only the HMAC over that signable string, then immediately trusts `request.shop` when constructing the metadata passed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm the check is `HMAC(secret, to_signable_string) == received_hmac`, with `to_signable_string` never including `shop`: [4](#0-3) 

The documented handler contract explicitly tells app developers to key tenant-specific work off `data.shop`: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac valid ⇒ (body, shop) both originated from Shopify for that shop`. In reality the binding only proves `hmac valid ⇒ body originated from Shopify for *some* shop using this app's secret`. Since the `client_secret` is shared by all shops that install the app, the shop attribution is entirely unauthenticated.

### Impact Explanation
Any merchant who installs the app (an "unprivileged" party with respect to every *other* tenant of the same app) can trigger a legitimate webhook for their own store, capture the resulting valid `(raw_body, hmac)` pair (e.g. via their own reverse proxy/logging in front of the app's public webhook endpoint, which they control since it is their own request), and replay it to the app's shared webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. `HmacValidator.validate` still succeeds because it never inspects the shop header, and `Registry.process` passes the attacker-chosen shop straight to the app's handler. This lets one tenant inject/spoof data or trigger tenant-scoped side effects (order/customer/product event processing, cache invalidation, billing triggers, etc.) attributed to a different, arbitrary shop — a cross-tenant confusion/injection primitive.

### Likelihood Explanation
Requires the attacker to be able to install the app on at least one shop (routine for any public/embedded Shopify app) and to observe one webhook delivery to their own installation's public endpoint, which is trivial since they control that endpoint. No access token, `client_secret`, or privileged account is needed beyond ordinary merchant self-service installation.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material, or independently verify that the shop header matches a shop that the app has a stored, previously-issued session/access token for before trusting `data.shop`. At minimum, document that `data.shop` is unauthenticated and must be cross-checked against known installed shops before being used for tenant-scoped logic.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both sharing the same app `client_secret`.
2. Attacker triggers `orders/create` on their own store; Shopify POSTs to the app's public webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac of body>`, and `raw_body`.
3. Attacker captures this `(raw_body, hmac)` pair (they own the receiving infrastructure for this request).
4. Attacker resends the identical `raw_body` and `hmac` to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) returns `true` because it only checks `raw_body` against `hmac`.
6. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: attacker_controlled_order_payload, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L12-29)
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
