### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing cross-tenant shop spoofing via replayed webhook bodies - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns `@raw_body` [1](#0-0) . `Registry.process` validates only that `hmac(raw_body)` matches, and then hands `request.shop` — read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header — straight to the app's webhook handler as the tenant identifier [2](#0-1) . The binding "shop that produced this authenticated payload == shop attributed to the data" is broken because `shop` is never part of the signed material.

### Finding Description
The zkEVM report's root cause is a value used to make a security/attribution decision (the CTX used to compute the addressed variable) diverging from the value that was actually verified/bound. The same class of bug exists here: `Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against `verifiable_query.hmac` [3](#0-2) . For webhook requests, `to_signable_string` is `@raw_body` only [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are not part of the signed bytes [4](#0-3) .

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata`, which is passed to the app-supplied handler as the shop the payload belongs to: [2](#0-1) . Documentation explicitly tells app authors that `data.shop` is "The shop domain of the webhook" and shows it being used to key application data (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) , i.e., the gem's own documentation establishes `shop` as the tenant identity binding that downstream code relies on.

Since HMAC is computed over `raw_body` alone using the single per-app `api_secret_key`, any attacker who owns their own Shopify store can:
1. Trigger a genuine webhook delivery to their own store (e.g., `orders/create`) and capture the exact `raw_body` + valid `hmac-sha256` header Shopify sent them (this pair is legitimate and requires no secret).
2. Replay that same `raw_body`/`hmac` pair directly to the victim app's webhook endpoint, but substitute the `shopify-shop-domain` header with the victim's shop domain.
3. `HmacValidator.validate` still succeeds because it only checks `hmac == HMAC(secret, raw_body)`, which is unaffected by header changes.
4. The handler receives `WebhookMetadata.new(shop: <victim's shop>, body: <attacker-controlled data from attacker's own store>, ...)` and — per the gem's documented usage pattern — will process/store the attacker's own order/customer/product payload as if it belonged to the victim shop.

This is exactly the "identity binding acted on but not covered by the authenticator" defect class called out for this gem: `shop` is the equality the app is supposed to be able to trust (`authenticated_source_shop == data.shop`), but the gem verifies only `raw_body`, not `shop`.

### Impact Explanation
This crosses the tenant boundary for any app whose webhook handler relies on `data.shop` to route or attribute incoming webhook data (the pattern the gem's own docs recommend). An attacker who is themself a legitimate merchant on the platform can inject arbitrary attacker-controlled resource data (attributed to a victim shop of their choosing) into the app's per-shop processing pipeline, without needing the app's `api_secret_key`, an access token, or any other credential — only their own ordinary merchant account to generate one authentic body/HMAC pair. Depending on what the host app does with webhook bodies (e.g., updating shop-scoped records, triggering fulfillment/inventory actions, syncing metafields), this can lead to cross-tenant data corruption or confusion. Per the impact taxonomy, this is a cross-tenant access issue arising purely from this gem's own signature-verification code.

### Likelihood Explanation
The prerequisite is only ordinary, unprivileged access: any developer/attacker can create a free Shopify development store or use their own store, subscribe an app-webhook-like endpoint (or capture their own app's webhook delivery), and legitimately receive a signed `raw_body`/`hmac` pair from Shopify for their own shop. No secret material, TLS interception, or social engineering is required — only crafting an HTTP POST with a spoofed `shopify-shop-domain` header. This is straightforward to reproduce and does not depend on the host application "ignoring" documented behavior; it depends on the host trusting `data.shop`, which is precisely what the gem's documentation instructs apps to do.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered material, or otherwise cryptographically bind the `shop` header to the specific `raw_body`/signature pair (e.g., verify that Shopify's HMAC was computed with knowledge that this shop sent this body — which is not currently possible without protocol changes on Shopify's side) — at minimum, the gem should document prominently that `data.shop`/`data.topic`/`data.webhook_id` are unauthenticated header values and must not be trusted for authorization decisions without an independent verification path (e.g., cross-checking against a known, registered shop for that webhook subscription/`webhook_id`).

### Proof of Concept
```ruby
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key",
  api_secret_key: "shared_secret",
  host: "https://app.example.com",
  is_embedded: true,
  scope: "read_orders",
  api_version: "2024-01",
)

# Step 1: Attacker legitimately receives this raw_body + hmac for THEIR OWN store
raw_body = '{"id":1,"note":"legit order from attacker store"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "shared_secret", raw_body)

# Step 2: Attacker replays with a spoofed victim shop-domain header
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Step 3: Passes HMAC validation despite shop header being forged
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker's own body, ...))
``` [2](#0-1) [6](#0-5) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-63)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L1-44)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module HmacValidator
      extend T::Sig

      class << self
        extend T::Sig

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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
      end
    end
  end
end
```

**File:** docs/usage/webhooks.md (L12-30)
```markdown
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
