This confirms the vulnerability: the gem's documentation explicitly instructs developers to trust `Registry.process` as verification that "the request did indeed come from Shopify," and to use `data.shop` as "The shop domain of the webhook" for tenant routing — but the `shop` field is never covered by the HMAC signature.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while the identifying `shop` value is read straight from the `x-shopify-shop-domain` HTTP header [2](#0-1) . `Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string` (i.e. the body) [3](#0-2) , so the shop-domain header is never cryptographically bound to the signature that `Registry.process` treats as proof of Shopify origin.

### Finding Description
`Registry.process` performs exactly one authenticity check — the HMAC over the body — and then immediately trusts `request.shop` (from the unauthenticated header) as the tenant identity that gets forwarded to the app's handler: [4](#0-3) 

The binding the gem is implicitly claiming to enforce is:
`HMAC-verified(shop) == request.shop`

But the actual binding enforced is only:
`HMAC-verified(raw_body) == true`, with `shop` parsed independently and unauthenticated.

Because the HMAC secret (`api_secret_key`) is shared across **all shops** installing a given app (it's the app's client secret, not a per-shop secret), an unprivileged internet user who can obtain one legitimately-signed `(raw_body, hmac)` pair — trivial for topics with static or predictable bodies, or simply by installing the app themselves as an attacker-controlled dev/test shop and capturing a real webhook — can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still passes (it never looked at the header), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` claiming the victim shop's identity [5](#0-4) .

The gem's own documentation reinforces that host apps are meant to rely on this binding: it describes `Registry.process` as verifying "the request did indeed come from Shopify" and describes `data.shop` as "The shop domain of the webhook" [6](#0-5) [7](#0-6) , with the example handler using `data.shop` directly as the tenant key (`shop_domain: data.shop`) [8](#0-7) .

### Impact Explanation
This is a cross-tenant identity confusion: an attacker can make the app process/attribute forged or replayed webhook data under a victim shop's identity despite passing the gem's authenticity check, because the shop identity field is not part of the signed payload the gem verifies. Any host application that follows the gem's documented pattern of trusting `data.shop`/`request.shop` post-`Registry.process` for tenant routing (job enqueuing, per-shop data writes, cache keys, etc., as shown in the gem's own example) is exposed to cross-tenant data corruption/injection.

### Likelihood Explanation
Requires only network access to the app's public webhook HTTP endpoint (no credentials, no access token, no `api_secret_key` needed) plus one captured or predictable `(raw_body, hmac)` pair. Many webhook topics have small, largely static bodies (e.g. `app/uninstalled` for a bare shop, or filtered/minimal-field registrations), and an attacker can always harvest a valid pair by installing the target app on their own store, making this practically achievable by any unprivileged internet actor who knows the target app's webhook callback path.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signed material, or independently verify that `request.shop` corresponds to a shop with a known, previously-established session/installation before trusting it, rather than deriving tenant identity solely from an unauthenticated header. At minimum, document prominently that `request.shop`/`data.shop` is *not* authenticated by `Registry.process` and must not be used as a sole tenant-binding key without additional verification (e.g., cross-checking against the shop associated with the resource IDs in the verified body).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a real webhook, e.g. `app/uninstalled`, capturing the raw body `B` and the valid header `x-shopify-hmac-sha256: H` (computed by Shopify with the app's shared `api_secret_key`) — this is a legitimate signature the attacker did not need to compute themselves.
2. Attacker sends a POST directly to the app's public webhook endpoint with:
   - body = `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid for `B`)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic`, `x-shopify-webhook-id` set as desired
3. `ShopifyAPI::Webhooks::Request.new` parses these headers [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-derives the HMAC from `B` [10](#0-9) .
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and any host-app logic that trusts this field for tenant attribution (as the gem's own documented example does) now acts on behalf of the victim shop using attacker-supplied data.

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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
