### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly from HTTP headers that are never included in the signed content. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then forwards the unauthenticated `shop` header value to the app's handler as the tenant identifier, breaking the binding: `shop authenticated (via HMAC) == shop acted on (routing key passed to handler)`.

### Finding Description
The webhook verification flow is:

1. `Registry.process` validates the request with `Utils::HmacValidator.validate(request)` [1](#0-0) 
2. `HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it with the `hmac` header value [2](#0-1) 
3. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the raw JSON body — nothing else [3](#0-2) 
4. `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, completely independent of the signed body [4](#0-3) 
5. After HMAC validation succeeds, `Registry.process` builds `WebhookMetadata` directly from `request.shop` and dispatches it to the app's handler, which the documentation explicitly says apps should use as the tenant/shop identifier for routing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [5](#0-4) [6](#0-5) 

The identity binding that should hold is: *the shop whose HMAC secret authenticated this request* == *the shop the app records/acts on*. Because the HMAC only covers the body, and the same `api_secret_key` is shared across every shop that installs the app, any party who can obtain one genuine, HMAC-signed webhook delivery (trivially done by installing the app on a shop they control and letting Shopify deliver a real webhook) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still return `true` (the body and HMAC are untouched), and `Registry.process` will pass the forged `shop` value on to the handler as if the event originated from that other shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who legitimately controls one shop installation of a multi-tenant app can impersonate an arbitrary other shop's webhook events (e.g. `orders/create`, `customers/data_request`, `app/uninstalled`, etc.) toward the app's backend, since the app has no library-provided mechanism to bind the verified body to a specific expected shop. Depending on what the handler does with `data.shop` (queue jobs, write data keyed by shop, trigger token revocation/mandatory compliance flows, etc.), this can lead to data being attributed to, or actions taken against, the wrong tenant — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop they control (which is the normal, low-privilege way any third party can use a public/embeddable Shopify app) and have network access to POST to the app's public webhook endpoint with custom headers — no `api_secret_key`, access token, or other privileged credential is required. Because the vulnerable behavior is intrinsic to the gem's `HmacValidator`/`Webhooks::Request` design (the shop header is never covered by the signature) rather than a host-application misuse, this is reachable from any deployment that follows the gem's documented webhook-processing pattern shown in `docs/usage/webhooks.md`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the material that is HMAC-verified, or provide an explicit API for the caller to assert/verify the expected shop domain against a value that is cryptographically tied to the request (Shopify does not sign headers, so at minimum the gem should document/require correlating `request.shop` against the caller's own list of currently-installed shops before trusting it, and could expose a way to compare it against session/store state). At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not authenticated by the HMAC and must be independently validated by the host app (e.g., checked against a known/installed-shops list) before being trusted for tenant routing.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they control) and triggers a webhook event (e.g. updates an order), causing Shopify to deliver a legitimate webhook to the app's HTTP endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed over `B` using the app's shared `api_secret_key`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker captures this request (e.g. via a proxy) and replays it to the same endpoint, keeping the body `B` and `X-Shopify-Hmac-Sha256: H` byte-for-byte identical, but changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com"...})` is constructed by the app per the documented pattern [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [3](#0-2)  and succeeds because `B` and `H` are unchanged.
5. `request.shop` returns the attacker-forged `"victim-shop.myshopify.com"` [8](#0-7) , and `Registry.process` passes this value into `WebhookMetadata` to the handler [9](#0-8) , which — following the documented handler pattern — will act on behalf of `victim-shop.myshopify.com` using attacker-controlled body content, despite the HMAC never having authenticated that shop association.

### Citations

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

**File:** docs/usage/webhooks.md (L127-135)
```markdown
```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
