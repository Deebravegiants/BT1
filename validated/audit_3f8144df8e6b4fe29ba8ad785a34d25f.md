This confirms the finding: `Registry.process` only validates the HMAC over the raw body via `Utils::HmacValidator.validate(request)`, then uses `request.topic` and `request.shop` — both of which come from HTTP headers (`x-shopify-topic`, `x-shopify-shop-domain`) that are **not** part of `to_signable_string` (which returns only `@raw_body`). [1](#0-0) [2](#0-1) [3](#0-2) 

Documentation confirms host apps trust `data.shop` as the tenant identifier for downstream work (e.g., enqueuing jobs `shop_domain: data.shop`) without any additional binding, since the gem's own contract is that `Registry.process` "will verify the request did indeed come from Shopify." [4](#0-3) [5](#0-4) 

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook attribution spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated for a specific merchant (`request.shop`) once `Utils::HmacValidator.validate(request)` passes. However, the HMAC signature only covers the raw request body (`to_signable_string` returns `@raw_body`), never the `x-shopify-shop-domain` / `shopify-shop-domain` header that the gem uses to populate `WebhookMetadata#shop`. The identity binding the gem's own documentation promises — "this will verify the request did indeed come from Shopify" and thereby that `data.shop` is trustworthy — does not actually hold, because `shop` is parsed but not verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`:

```ruby
sig { override.returns(String) }
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop` is read straight from a header, entirely outside `to_signable_string`:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [6](#0-5) 

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it with `verifiable_query.hmac`:

```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [7](#0-6) 

`Registry.process` then dispatches to the app's handler using the unverified `request.shop`:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [2](#0-1) 

The identity equality that the gem implicitly claims to enforce is:
`shop_the_HMAC_authenticates == shop_the_handler_acts_on`

In reality the equality that holds is only:
`raw_body_the_HMAC_authenticates == raw_body_the_handler_parses`

`shop` (and `topic`, `api_version`, `webhook_id`) are unauthenticated header values that ride along unchecked. Any actor who can produce one valid `(raw_body, hmac)` pair for a topic — which any merchant installing the app naturally can, simply by triggering a webhook-worthy event on their own store (e.g. `orders/create`) and capturing the delivery to their own endpoint — can resubmit that exact same body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `Registry.process` will accept it as valid (the body/HMAC match) and hand the app's handler a `WebhookMetadata` claiming the payload belongs to a different, victim shop.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem is supposed to enforce. Per the documented usage pattern, apps enqueue background jobs keyed on `data.shop` (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), and typically use `data.shop` to look up the corresponding stored `Session`/access token or to write records against that shop's data. An attacker who controls a shop (an ordinary, unprivileged merchant with no special access to the target) can inject arbitrary attacker-controlled body content that is falsely durable/attributed to a victim shop of their choosing, causing the host application to process, store, or act on forged data under a different tenant's identity — a cross-tenant data-integrity/confused-deputy issue rooted entirely in this gem's `Webhooks::Request`/`Registry` design, since the gem is the only place doing (incomplete) authentication of the shop-to-payload binding.

### Likelihood Explanation
Likelihood is bounded by the fact that Shopify does not sign the shop-domain header itself, and only apps whose webhook path is discoverable/guessable and who don't perform any additional shop existence/ownership check on `data.shop` are exposed. However, exploitation requires no secrets, tokens, or privileged access at all — only the ability to install the target app on any shop (which is by definition open to any merchant) and replay a captured, unmodified `raw_body`+`hmac` pair with a substituted header. This is fully within reach of an unprivileged internet user and directly exploits a gap in the gem's own HMAC-verification contract rather than any host-application misuse.

### Recommendation
Bind the shop domain into the signed material, or otherwise cryptographically tie `shop` to the verified body. Concretely, extend `VerifiableQuery`/`to_signable_string` for webhook requests (or add a dedicated check) so that the HMAC computation, or an equivalent verification step, incorporates the `shop-domain` header value itself, so that changing it invalidates the signature — mirroring the way `Auth::Oauth::AuthQuery#to_signable_string` deliberately folds `shop` into its signed payload. At minimum, document prominently that `data.shop`/`data.topic`/`data.webhook_id` are NOT authenticated by the HMAC check and that host apps must independently confirm the claimed shop actually owns/is entitled to the delivered `webhook_id`/topic (e.g. by cross-checking against Shopify's Admin API) before trusting it for any tenant-sensitive action.

### Proof of Concept
```ruby
# Attacker owns shop "attacker-shop.myshopify.com" and has installed the target app.
# They trigger any subscribed webhook (e.g. orders/create) on their own store and
# capture the raw POST the app's webhook endpoint receives from Shopify, e.g.:
raw_body = '{"id":1,"note":"forged content"}'
valid_hmac_b64 = "<HMAC(app_secret, raw_body), captured verbatim from the real Shopify delivery>"

# The attacker now resends the exact same body + HMAC to the same endpoint,
# but swaps only the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,   # unchanged, still matches raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed_body, ...))
# The app's handler now processes attacker-controlled data as if it belongs to victim-shop.
```

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
