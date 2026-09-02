## Finding

Webhook authenticity in this gem is verified only over the **raw request body** — the `shop`, `topic`, `webhook-id`, and `api-version` values used to route and attribute the webhook are taken from **unauthenticated HTTP headers** that are not covered by the HMAC signature.

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not bound to the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate_signature` computes/compares the HMAC solely over that body string using the app's single, shop-independent `api_secret_key`. [1](#0-0) [2](#0-1) 

Meanwhile, `Registry.process` trusts `request.shop`, `request.topic`, and `request.webhook_id` — all parsed straight from headers, never included in the signed bytes — and hands them to the app's handler as authenticated tenant identity: [3](#0-2) [4](#0-3) 

Because a single app secret (`Context.api_secret_key`) is shared across every merchant shop that installs the app, an unprivileged user who controls their own Shopify store (an "unprivileged internet user" relative to any *other* tenant) can trigger a real webhook for their own shop, capture the valid `(raw_body, hmac)` pair Shopify sends, and replay it directly to the app's public webhook endpoint with the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header rewritten to point at a victim shop. `HmacValidator.validate` still succeeds because it only checks the untouched body against the (shop-agnostic) secret, so `Registry.process` calls the handler with `WebhookMetadata` claiming the event belongs to the victim shop.

### Finding Description
The identity binding that should hold is:
`shop asserted in the (HMAC-)authenticated request == shop the handler/business logic acts on`

Here, the equality is broken: the HMAC only authenticates *that the app's secret produced this body*, not *which shop this body/header set belongs to*. `shop` is verified nowhere against the signature — it is merely read out of a header that any HTTP client can set. [5](#0-4) 

Before attack: legitimate webhook for shop A → `raw_body_A`, `hmac_A = HMAC(secret, raw_body_A)`, header `shop-domain: A`.
After attack: attacker resends `raw_body_A` + `hmac_A` unchanged, but sets header `shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` re-derives `HMAC(secret, raw_body_A)`, which still equals `hmac_A`, so validation passes. `Registry.process` then dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler. [6](#0-5) 

Downstream host applications are documented by this gem to trust `Registry.process`'s guarantee that "the request did indeed come from Shopify," and to key session/data lookups off the delivered `shop` field: [7](#0-6) 

### Impact Explanation
This crosses a tenant boundary: an attacker with only their own (unprivileged) shop installation can make the app process arbitrary attacker-controlled webhook payload content while attributing it to any other shop known to have installed the app. Depending on the handler logic (which the gem's own docs instruct apps to key by `data.shop`), this can cause cross-tenant data corruption, spoofed lifecycle events (e.g. forged `app/uninstalled`, `shop/redact`, `customers/data_request`), or state confusion tied to the victim shop's session — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only: (1) installing the app on the attacker's own shop (self-service, unprivileged), (2) triggering one event to obtain a valid `(body, hmac)` pair, and (3) sending a raw HTTP POST to the app's public webhook route with a modified `shop-domain` header — no access token, secret, or privileged account needed.

### Recommendation
Include the identity fields (`shop`, `topic`, and ideally `webhook_id`) in the bytes covered by the HMAC check, or independently verify that the `shop-domain` header corresponds to a shop with a known/authorized installation before dispatching to handlers, rather than trusting header-only values that sit outside the signed payload.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify.
2. POST that same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and any desired `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `raw_body`. The handler executes with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>)`. [8](#0-7)

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

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
```
