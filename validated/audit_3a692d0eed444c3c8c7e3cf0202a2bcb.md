Confirmed: `WebhookHandler.handle` receives `WebhookMetadata` built directly from `request.shop`/`request.topic` (unauthenticated headers), while `HmacValidator.validate` only checks `request.to_signable_string`, which returns `@raw_body` alone.### Title
Webhook shop-domain/topic identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the raw JSON body against the `X-Shopify-Hmac-SHA256` header, then unconditionally trusts the `shop-domain` and `topic` headers when constructing the `WebhookMetadata` passed to the app's handler. Because the `shop`/`topic` fields are never part of the signed material, any request carrying a *valid* body+HMAC pair (computed with the app's own `api_secret_key`, which is shared across every merchant that installs the app) can claim to originate from an arbitrary shop, breaking the tenant-identity binding the handler relies on.

### Finding Description
`HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the supplied `hmac`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw HTTP body — it does **not** include the `shop`, `topic`, `webhook_id`, or `api_version` values that are pulled from HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC and, if it passes, builds `WebhookMetadata` directly from those unsigned header-derived fields (`request.shop`, `request.topic`), then dispatches it to the app-supplied handler: [3](#0-2) 

The identity binding that should hold is:
`HMAC_valid(body, secret) == true` **iff** `shop_header == shop_that_secret_actually_belongs_to`.

In reality the code only proves `HMAC_valid(body, secret) == true`; the `shop` (and `topic`) values are asserted, not verified. Since `api_secret_key` is a single per-app secret shared by every merchant who installs the app (not a per-shop secret), any unprivileged internet user who installs the app on their own free/dev store will legitimately receive real webhook deliveries — genuine `(raw_body, hmac)` pairs signed with that same app-wide secret. That attacker can replay the exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds (the body wasn't altered), and the handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker_controlled_json, topic: attacker_chosen_topic)`, i.e., attacker-controlled data attributed to a tenant the attacker does not control. This is documented in `docs/usage/webhooks.md` as the mechanism apps use to key persistence/authorization by `data.shop`: [4](#0-3) 

### Impact Explanation
This breaks the tenant/shop identity boundary the gem is supposed to enforce for webhook processing — it is exactly the class of "field acted on but not covered by the HMAC" bug: `shop`/`topic` are consumed by application logic (persistence keyed by shop, `perform_later(shop_domain: data.shop, ...)` per the docs) without being bound to the cryptographic proof of authenticity. Any app built on this gem that trusts `data.shop` for tenant scoping (exactly as the shipped docs recommend) can have another one of its own merchants inject fabricated webhook events/data attributed to an arbitrary other shop — a cross-tenant data-integrity/impersonation issue.

### Likelihood Explanation
Exploitation requires no compromise of the target: the attacker only needs to be a legitimate, unprivileged installer of the same app (any merchant/dev store can install a public/dev app) to receive genuine `(body, hmac)` pairs signed with the shared `api_secret_key`, then replay them with a modified `shop-domain`/`topic` header to the app's public webhook callback endpoint. No access to the victim's access token, the app's `client_secret`-holder infrastructure, or TLS interception is needed.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (or otherwise cryptographically bind them to the raw body, e.g., by adding them to `to_signable_string` and requiring Shopify to compute the HMAC over the concatenation), or, at minimum, require the host app to cross-check `request.shop` against a shop that is expected/known-installed before trusting it. At the very least the header-derived `shop`/`topic` fields should be treated as unauthenticated inputs in the library's own documentation and API surface, since currently `Registry.process`/`WebhookMetadata` present them as if implicitly validated by the preceding `HmacValidator.validate` call.

### Proof of Concept
```ruby
# Attacker installs the target app on their own store "attacker.myshopify.com"
# and receives a genuine webhook from Shopify, e.g. for "orders/create":
raw_body = '{"id":1,"note":"legit"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker replays the SAME body/hmac to the app's webhook endpoint,
# but spoofs the shop-domain header to a victim shop they do not control:
headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(real_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id"  => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (body unaltered),
#    handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", ...)) is invoked,
#    even though the request has nothing to do with victim-shop.
```

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
