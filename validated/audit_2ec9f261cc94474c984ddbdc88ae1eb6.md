Confirmed root cause: the webhook `hmac` binding covers only `to_signable_string` (the raw request body), while `shop` and `topic` are read directly from unauthenticated HTTP headers and passed straight to the handler as the tenant identifier.### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  yet `Registry.process` uses `Utils::HmacValidator.validate(request)` (which validates that signable string against the HMAC) as the sole authenticity check before trusting `request.shop` and `request.topic`, which are read straight from unauthenticated HTTP headers [2](#0-1)  and passed directly to the app's handler as the tenant identifier [3](#0-2) .

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it against the `hmac` field with `OpenSSL.secure_compare` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers via `shopify_header` with zero cryptographic binding to the HMAC [5](#0-4) .

`Registry.process` validates only the HMAC of the body, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic` and dispatches it to the app's registered handler for that topic [3](#0-2) . The library's own documentation instructs app authors to use `data.shop` as the tenant/shop identifier for downstream processing (e.g. `shop_domain: data.shop`) [6](#0-5) , and states that `Registry.process` "will verify the request did indeed come from Shopify" [7](#0-6)  — implying the header-derived `shop` is trustworthy, when in fact it is not bound by the signature at all.

Binding that should hold but does not: `hmac == HMAC(api_secret_key, shop || topic || body)`; instead only `hmac == HMAC(api_secret_key, body)` holds, i.e. the equality `authenticated_shop == shop_acted_on` is never enforced.

Because a single app's `api_secret_key` is shared across every shop that installs the app, any unprivileged attacker who controls one shop that has the app installed can legitimately receive a webhook delivery with a valid `(raw_body, hmac)` pair for that body. Because `topic`/`shop-domain` headers are not part of the signed content, the attacker can replay that exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain. `Registry.process` will still pass HMAC validation (since the body is unchanged) and will dispatch to the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, causing the host application to attribute attacker-controlled data to another tenant.

### Impact Explanation
This breaks the tenant identity binding at the exact class of bug in scope ("shop authenticated versus shop stored as a session key" / "a field acted on but not covered by the HMAC"). Any app that uses `data.shop` (as documented) to key session lookups, database writes, or business logic will process forged data under a victim shop's identity — this is cross-tenant access/data injection achieved purely by an internet-reachable POST to the app's public webhook route, requiring no access token, `client_secret`, or privileged account. This satisfies the Critical impact bar ("cross-tenant access").

### Likelihood Explanation
Likelihood is realistic: an attacker needs only (a) their own store with the target app installed (any developer/free/trial store qualifies) to legitimately harvest one valid `(raw_body, hmac)` pair for a chosen topic, and (b) the ability to send an HTTP POST with custom headers to the app's public webhook endpoint — both trivially available to an unprivileged internet user. No knowledge of `api_secret_key` is required because the attacker never needs to compute an HMAC; they replay one Shopify itself already computed for their own shop's delivery.

### Recommendation
Bind `shop` (and ideally `topic`) into the HMAC-signable representation, or independently verify the `shop-domain` header against an authenticated source (e.g., cross-check against the shop associated with the webhook subscription/session, or validate through `ShopifyAPI::Utils::ShopValidator` combined with a server-side registry lookup keyed by an authenticated identifier) before trusting `WebhookMetadata#shop` for tenant-scoped operations. At minimum, update `Webhooks::Request#to_signable_string` so the signed payload used for verification incorporates the header-derived identity fields that `Registry.process` relies on, closing the gap between "bytes verified" and "bytes acted on."

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook subscribed by the app (e.g. `orders/create`). Shopify delivers a POST with a genuine `raw_body` and a valid `x-shopify-hmac-sha256` computed over that body using the app's shared `api_secret_key`.
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker sends a new POST directly to the app's public webhook endpoint (the same route registered via `add_registration`) with:
   - `x-shopify-hmac-sha256`: unchanged (still valid for `raw_body`)
   - body: unchanged `raw_body`
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com`
   - `x-shopify-topic`: unchanged (or another topic handled by the app)
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks required headers are present) [8](#0-7) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [3](#0-2) .
6. The handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
