This confirms the vulnerability: the webhook HMAC only signs the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are taken from unauthenticated headers and passed unmodified to the handler after only the body-HMAC succeeds.

### Title
Webhook HMAC only covers the request body, letting an attacker spoof the `shop` (tenant) identity delivered to handlers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `ShopifyAPI::Utils::HmacValidator.validate` only authenticates the body bytes and never binds the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers to that signature [2](#0-1) . `Registry.process` validates the HMAC and then dispatches to the handler using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` taken straight from those unauthenticated headers [3](#0-2) .

### Finding Description
The intended identity binding is: `shop` value delivered to `WebhookMetadata` == the shop that Shopify's HMAC actually authenticated for this payload. In reality, `HmacValidator.compute_signature` is computed only over `verifiable_query.to_signable_string`, and for `Request` that string is just the raw body [4](#0-3) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers with no cryptographic coverage [5](#0-4) .

Because a merchant who has installed the app on their own store legitimately receives real webhook deliveries (valid body + valid HMAC digest of that body, signed with the app's shared secret) for their own shop, they can capture one such delivery and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (and/or `webhook-id`/`api_version`) value. Since the HMAC never covered that header, `Utils::HmacValidator.validate(request)` still returns `true` [6](#0-5) , and `Registry.process` calls the handler with the forged `shop` value [7](#0-6) .

As documented, the gem explicitly instructs host apps to trust `data.shop` from `WebhookMetadata` to identify which tenant the webhook belongs to (e.g., to enqueue tenant-scoped jobs) [8](#0-7) , and the test suite confirms `data.shop` is populated verbatim from the `shopify-shop-domain` header without any cross-check against the HMAC-covered body [9](#0-8) .

### Impact Explanation
This breaks the tenant-identity binding the gem is trusted to enforce: `Registry.process` presents body-authenticated data as if it were also shop-authenticated. A host application that (as documented) uses `data.shop` to select which merchant's session/database record to update, or to attribute the webhook's side effects, can be made to apply another shop's legitimate webhook data under an attacker-chosen shop identity, or vice versa — a cross-tenant data-confusion vector reachable by any unprivileged merchant who has installed the app once.

### Likelihood Explanation
Any actor who can install the app on a shop they control (or otherwise capture one valid webhook body+HMAC pair, e.g. `shop/redact` or any subscribed topic) can trivially replay it with a modified shop header using nothing more than a HTTP client — no access token, `client_secret`, or privileged access is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material, or independently verify that the `shopify-shop-domain` header corresponds to a shop the app actually has a stored/active session for before dispatching to the handler; at minimum, document/require host apps to cross-check `request.shop` against the shop that owns the webhook subscription id looked up from Shopify (already partially supported via `get_webhook_id`) rather than trusting the header directly.

### Proof of Concept
1. Install the app on shop A (`attacker.myshopify.com`) and receive a real webhook delivery: body `B`, header `shopify-hmac-sha256: H` (a valid HMAC of `B` with the shared secret), and `shopify-shop-domain: attacker.myshopify.com`.
2. Replay the same `B` and `H` to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim.myshopify.com"})` is constructed; `to_signable_string` still returns `B`, so `Utils::HmacValidator.validate` succeeds [1](#0-0) .
4. `Registry.process` calls the registered handler with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)` [7](#0-6) , causing the host app to process attacker-controlled data under the victim shop's identity.

### Citations

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

**File:** docs/usage/webhooks.md (L10-26)
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
```

**File:** test/webhooks/registry_test.rb (L284-301)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)

        assert(handler_called)
```
