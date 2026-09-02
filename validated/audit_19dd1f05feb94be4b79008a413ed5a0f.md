This confirms the root-cause chain. This is a genuine, reachable identity-binding gap in this gem's own code.

### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Utils::HmacValidator.validate` signs/verifies only that body against `Context.api_secret_key` [1](#0-0) [2](#0-1) . The `shop` field returned by `Request#shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header and is never included in the signed payload [3](#0-2) . `Registry.process` validates only the HMAC of the body, then forwards `request.shop` verbatim into `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Finding Description
The security guarantee an app relies on is: *"the shop that authorized this webhook data" == "the shop reported in `WebhookMetadata.shop`."* That equality is never enforced by the gem. The HMAC only binds the request body to the app's shared `api_secret_key` (a single secret used across every shop that installs the app) — it says nothing about which shop the body pertains to. Because `client_secret`/`api_secret_key` is identical for all merchants of a given app, any two webhook payloads for the same app produce comparable, independently-valid HMACs regardless of which shop originated them. An attacker who can obtain one legitimately-signed webhook body+HMAC pair (trivially available to anyone who installs the target app on their own store, since webhooks are delivered over plain HTTP(S) POST to app-controlled endpoints and the shop domain header is attacker-visible/attacker-controlled at the HTTP layer) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it only recomputes the signature over `@raw_body`, never over the shop header [5](#0-4) . `Registry.process` has no additional check that ties `request.shop` to the verified content, so `handler.handle` is invoked with a `WebhookMetadata.shop` that the attacker fully controls [6](#0-5) . This is precisely the documented, intended way for host apps to identify which tenant a webhook update belongs to [7](#0-6) , so an app following the gem's own documentation ends up trusting an unauthenticated field for tenant attribution.

### Impact Explanation
This breaks the shop-authenticated vs. shop-acted-upon identity binding, which the rules classify as Critical/High-impact cross-tenant access: an attacker can cause an app to process (and typically persist/act upon) webhook data while attributing it to a victim shop the attacker never installed the app on, corrupting per-tenant data, triggering tenant-scoped side effects (e.g., billing, inventory sync, order fulfillment automation) for a shop under attacker control.

### Likelihood Explanation
Requires the attacker to install the app themselves (common for public apps) to obtain one valid signed webhook, then replay it with a forged shop header to the app's public webhook endpoint — no access token, `client_secret`, or privileged credentials of the victim are needed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed content, or otherwise require the host application to cross-check `request.shop` against a shop already known/authorized (e.g., an existing session) before trusting it, and document that `request.shop`/`WebhookMetadata.shop` is not currently covered by HMAC verification.

### Proof of Concept
```ruby
secret = ShopifyAPI::Context.api_secret_key
body = '{"id":1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body)
hmac_b64 = Base64.encode64(hmac)

# Attacker legitimately obtains this pair from their OWN installed shop:
legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# Attacker replays identical body+hmac, only swapping the shop header:
forged_headers = legit_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) returns true (only body is checked),
# handler.handle receives WebhookMetadata.shop == "victim-shop.myshopify.com"
```

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
