Based on my analysis, this is the key finding: the library's `Registry.process` call states it "will verify the request did indeed come from Shopify and then call the specified handler," and the documentation explicitly instructs the handler to trust `data.topic` and `data.shop` for routing/business logic — yet the HMAC only covers the raw body, not the `topic`, `shop-domain`, `webhook-id`, or `api-version` headers.

### Title
Webhook topic/shop/id headers are not covered by HMAC verification, enabling tenant and topic spoofing via header manipulation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `topic`, `shop`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [1](#0-0) . `Registry.process` validates only the HMAC over that signable string and then dispatches the handler using the unverified header-derived `topic` and `shop` values [2](#0-1) .

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, signable_string)` where `signable_string` should cover every field the handler acts on. Here it only covers `raw_body`; `topic`, `shop`, `webhook_id`, and `api_version` are excluded from the signed content [3](#0-2) . `Utils::HmacValidator.validate` recomputes the signature purely from `to_signable_string` and compares it to the `hmac` header using the app's shared `api_secret_key` (the same secret for every shop that installs the app) [4](#0-3) . Because the secret is shared across all tenants of the app, any tenant who can obtain one valid `(raw_body, hmac)` pair for a webhook to their own shop can replay it while substituting the `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` headers, and `HmacValidator.validate` still returns `true` since it never inspects those headers. `Registry.process` then builds `WebhookMetadata` directly from these spoofed headers and invokes the topic handler as if the event legitimately originated from the spoofed shop/topic [5](#0-4) . This breaks the equality `shop_verified_by_hmac == shop_acted_on_by_handler`.

### Impact Explanation
This gives cross-tenant impact: an app receiving webhooks for many merchant shops can be tricked into attributing another shop's webhook event (or a different topic's event, e.g. `app/uninstalled` reinterpreted as `orders/create` or vice versa) to a spoofed tenant. Depending on the host handler's logic (which the library's own docs instruct to key business logic off `data.shop` and `data.topic`) [6](#0-5) , this can lead to cross-tenant data confusion/corruption driven entirely by an unprivileged/self-installed tenant forging headers on a replayed, validly-signed payload — without ever needing the app's `client_secret`.

### Likelihood Explanation
Medium: the attacker must possess at least one valid `(raw_body, hmac)` pair, which any merchant who installs the app can trivially obtain by triggering a webhook to their own shop (e.g., an `app/uninstalled` or other webhook with a small/predictable body). They then only need to change unauthenticated HTTP headers on their replayed HTTP POST — no cryptographic material is required. Practical exploitation is bounded by whether the replayed body content is meaningful once relabeled with a different topic, but the underlying binding failure is unconditional.

### Recommendation
Include `topic`, `shop`, and `webhook_id` (and any other header fields the handler acts upon) in the HMAC-signed content, or otherwise cryptographically or out-of-band bind the header values to the specific request before dispatching to `handler.handle`. At minimum, `Registry.process` should independently verify that `request.shop` corresponds to a shop with an active, matching webhook registration/session before invoking the handler, rather than trusting the header value.

### Proof of Concept
```ruby
# Attacker legitimately installs the app on shop-a.myshopify.com and captures
# a real Shopify webhook delivery for it:
raw_body = '{}'
real_hmac = "shopify-computed-hmac-for-shop-a-app_uninstalled"

headers = {
  "x-shopify-topic" => "orders/create",          # spoofed topic
  "x-shopify-hmac-sha256" => real_hmac,          # unchanged, still validates
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed tenant
  "x-shopify-webhook-id" => "attacker-chosen-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) only checks HMAC(raw_body); it passes.
# The handler for "orders/create" is invoked with shop: "victim-shop.myshopify.com".
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-63)
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
