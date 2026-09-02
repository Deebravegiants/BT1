This confirms the identity binding break: `ShopifyAPI::Webhooks::Request` treats the `shop` (and `topic`, `webhook_id`, `api_version`) as trusted attributes read directly from HTTP headers, while `to_signable_string` (used by `Utils::HmacValidator.validate`) only signs the raw request body [1](#0-0) . `Registry.process` validates the HMAC and then passes `request.shop` straight into `WebhookMetadata` for the handler, without any cross-check that the shop is bound to the signed body [2](#0-1) . The library's own docs confirm handlers are expected to trust `data.shop` for tenant identification (e.g., `shop_domain: data.shop`) [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, so the `x-shopify-shop-domain` header (exposed via `Request#shop`) is never included in the HMAC computation performed by `Utils::HmacValidator.validate`. Any party who can obtain one validly-signed webhook payload for an app (e.g., by installing the app on their own store and receiving a webhook with a predictable/empty body) can replay that exact body while swapping the `shop-domain` header to any other shop, and `Registry.process` will accept it as authentic and hand `WebhookMetadata` with the attacker-chosen shop to the app's handler.

### Finding Description
The HMAC binding equality that should hold is: `shop_the_HMAC_was_computed_for == shop_the_handler_acts_on`. In this gem that equality is broken:

- `Request#to_signable_string` returns only `@raw_body` [4](#0-3) .
- `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from attacker-controllable HTTP headers, independent of the signed body [5](#0-4) .
- `HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e., the body only, using the app's single shared `api_secret_key` (the same secret is used for every shop that has installed the app) [6](#0-5) .
- `Registry.process` validates HMAC over the body, then immediately trusts `request.shop` to construct `WebhookMetadata`, which is delivered to the app's handler as the shop identity for the event [2](#0-1) .

Because the secret is shared across all shops for a given app, and the shop identity is carried in an unsigned header, a valid HMAC for shop A's webhook body is equally "valid" if replayed with shop B's `shop-domain` header — the signature says nothing about which shop it belongs to. Many webhook topics have small or fixed-shape bodies (illustrated by the test suite using `"{}"` as a raw body for various topics) [7](#0-6) , making body reuse across shops trivial for an attacker who is a legitimate (if low-privilege) merchant with the app installed on their own store and can capture their own genuine webhook deliveries.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged user who has the app installed on their own shop can forge webhook deliveries that the host application attributes to a victim shop, because the gem's `WebhookMetadata.shop` is not bound to the HMAC that authenticates the payload. Depending on how the host app uses `data.shop` (as the docs recommend, e.g. `shop_domain: data.shop` for enqueuing background jobs) [8](#0-7) , this can trigger cross-tenant side effects such as incorrectly triggering GDPR data-erasure, app-uninstall cleanup, or other shop-scoped state changes against a victim shop's data using an attacker-controlled/replayed body — a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires only that the attacker be a merchant with the target app installed (a routine, unprivileged precondition — no leaked secrets or special access needed), and knowledge/capture of one webhook body they legitimately received. Because the HMAC computation is entirely independent of the shop header, no cryptographic material needs to be forged — only the header needs to be swapped in the replayed HTTP request.

### Recommendation
Bind the shop identity into the value that is authenticated. Options:
- Include the `shop-domain` (and ideally `topic`/`webhook_id`) header value in `to_signable_string`, though this changes wire compatibility with Shopify's actual signing scheme, or (preferably)
- Since Shopify's HMAC only ever covers the raw body by design, the gem should not expose `Request#shop` as an implicitly "authenticated" field. At minimum, document prominently that `data.shop` returned via `Registry.process` is unauthenticated header data, and require/recommend that host applications independently verify the shop against the body's embedded shop identifier (most Shopify webhook bodies include the shop's numeric/global ID) or cross-check against a known/expected shop for the specific delivery URL before using it as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook, e.g. topic `app/uninstalled` with raw body `{}` and a valid `x-shopify-hmac-sha256` header computed over `{}` using the app's shared `api_secret_key`.
2. Attacker replays the exact same body (`{}`) and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `raw_body` (`{}`) and successfully matches, since the shop header was never part of the signed string [4](#0-3) [9](#0-8) .
4. `Registry.process` builds `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim.myshopify.com", ...)` and invokes the app's handler with `victim.myshopify.com` as the shop, even though the request was never sent by Shopify on behalf of that shop [10](#0-9) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** test/webhooks/registry_test.rb (L16-30)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```
