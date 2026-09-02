This confirms the analog: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verifies body integrity only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers and are never part of the signed content. `Registry.process` at `lib/shopify_api/webhooks/registry.rb:189-199` validates only the HMAC over the body and then trusts `request.shop`/`request.topic` unconditionally, passing them into `WebhookMetadata` for the app's handler, which per the gem's own docs (`docs/usage/webhooks.md`) is expected to key tenant-scoped logic off `data.shop`.

### Title
Webhook shop/topic/webhook_id/api_version headers are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the HMAC over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that the registry treats as authenticated come exclusively from unsigned HTTP headers. A holder of any one genuine, validly-signed webhook (e.g., from their own store) can replay it with a modified `shop-domain` header to impersonate any other merchant to the app's handler.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
and `shop`, `topic`, `webhook_id`, `api_version` are read directly from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` (used by `Registry.process`) computes the signature strictly over `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` checks only this body HMAC, then unconditionally forwards `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) into `WebhookMetadata`, which is delivered to the app's `WebhookHandler.handle`: [4](#0-3) 

Because Shopify uses **one shared HMAC secret (`api_secret_key`) across all shops that have the app installed**, any user who installs the app on their own store receives genuinely-signed webhook deliveries. Since the signature only covers the JSON body and never the `shop-domain` header, that user can capture a legitimate `(body, hmac)` pair from their own shop and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to any victim shop domain. `HmacValidator.validate` still returns `true` because it only checks the body against the shared secret; `Registry.process` never independently verifies that the claimed `shop` actually originated the request. The equality that should hold — `shop asserted to handler == shop that produced/authorized this exact payload` — is broken: the binding is really `hmac verifies body` while `shop` is taken from an attacker-controlled, unsigned header.

The gem's own documentation confirms downstream apps are expected to trust `data.shop` as the authenticated tenant identifier for enqueuing/processing work: [5](#0-4) 

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (if unprivileged) installer of the app on their own shop can make the app believe a webhook payload originated from a different, victim shop. Depending on how the host application uses `data.shop` (e.g., looking up the victim's stored access token/session to act on their behalf, writing data keyed by shop, or triggering side effects scoped to the victim tenant), this enables cross-tenant data injection/corruption using the attacker's own (attacker-authored) body content, but falsely attributed to the victim's shop. This matches the High-severity "cross-tenant access" criterion.

### Likelihood Explanation
High. No special privileges are needed beyond installing the app on one's own store (a normal, unprivileged action), and capturing/replaying an HTTP webhook request with a modified header is trivial. The vulnerable code path (`Registry.process`) is the gem's documented, standard mechanism for consuming webhooks.

### Recommendation
Bind the identity fields to the HMAC by including `shop`, `topic`, `webhook_id`, and `api_version` in the signable string (or otherwise cryptographically bind them, e.g. by re-deriving/confirming shop identity via a signed channel such as a stored per-shop token) rather than trusting raw, unsigned headers. At minimum, `Registry.process` should reject requests where the claimed `shop` cannot be corroborated against known/registered shops for the app, or the signable string used for HMAC verification should incorporate the headers that `Registry.process` subsequently trusts.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, obtaining genuine webhook deliveries signed with the app's shared `api_secret_key`.
2. Attacker captures one such delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `HMAC-SHA256(api_secret_key, B) == H`), along with headers `X-Shopify-Topic`, `X-Shopify-Webhook-Id`.
3. Attacker resends a new HTTP request to the app's webhook endpoint with the identical body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` decodes `H` and whose `shop` returns `"victim-shop.myshopify.com"`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and compares to `H` — this succeeds because `B` and `H` are unchanged from the genuine attacker-shop webhook.
6. The registry proceeds to call `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))`, causing the app to process attacker-controlled `body` content as if it were an authentic webhook from `victim-shop.myshopify.com`.

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
