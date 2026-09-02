### Title
Webhook shop-domain and topic headers are trusted for tenant identification without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — read from HTTP headers — are never included in the signed payload and are handed to the app's handler as trusted tenant-identifying data.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), separate from the `hmac` value: [1](#0-0) 

Its `to_signable_string` — the bytes actually covered by the HMAC — is defined as only the raw body, excluding all headers: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC strictly over `to_signable_string` (the body): [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which were part of the verified bytes — to the app-supplied handler as authenticated metadata: [4](#0-3) 

The documented equality the gem is supposed to enforce is: `bytes verified by HMAC == bytes that determine the tenant (shop) the webhook is attributed to`. In this implementation that equality does not hold — the verified bytes are `raw_body` only, while the tenant-identifying `shop` field comes from an unauthenticated header. The gem's own documentation confirms `shop` is expected to be a trusted output of `process`, telling integrators to key their per-tenant business logic off `data.shop`: [5](#0-4) 

### Impact Explanation
Because the HMAC does not bind the `shop-domain` header, a party who can obtain one genuine, validly-signed webhook payload (e.g. an attacker who owns/controls a store using the same app and thus receives real webhooks with a real HMAC for that shop) can replay the identical `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value. `HmacValidator.validate` will still succeed, because it only checks the body signature, and `Registry.process` will pass the attacker-chosen `shop` value straight to the handler as if Shopify itself had attributed the payload to that shop. Any app that uses `data.shop` from `WebhookMetadata` (as this gem's own documentation instructs) to select which merchant's records to update will process/attribute data under the wrong tenant — a cross-tenant integrity violation reachable by an unprivileged party who merely needs access to one legitimate webhook delivery (their own store's), not the app's `client_secret` or any privileged credential.

### Likelihood Explanation
Likelihood is moderate: exploitation requires the attacker to first obtain at least one authentic (body, HMAC) pair, which is achievable for anyone who installs the app on a shop they control and thus legitimately receives real webhooks with valid signatures. From there, replaying with a forged `shop-domain` header is trivial and entirely within reach of an unprivileged internet user with no access to the app's secret, tokens, or infrastructure.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the HMAC-signed material, or independently verify that `request.shop` corresponds to a shop that Shopify's delivery infrastructure is authorized to send to (e.g., cross-check against the shop associated with the webhook subscription/session) before handing it to the handler. At minimum, document prominently that `data.shop` from `WebhookMetadata` is not itself authenticated by the HMAC check and must be validated independently by the integrating app before being trusted for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and legitimately receives a real webhook delivery for topic `orders/create`, with raw body `B` and valid header `shopify-hmac-sha256: H` (computed by Shopify over `B` using the app's real secret).
2. Attacker replays the exact same request to the app's webhook endpoint, keeping `raw_body: B` and `shopify-hmac-sha256: H` unchanged, but replacing the header `shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (all required headers present). [6](#0-5) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`= B`) and matches `H` — validation passes despite the forged shop header. [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` is `"victim-shop.myshopify.com"` — data legitimately belonging to `attacker-shop` is now processed and attributed by the app as belonging to `victim-shop`. [8](#0-7)

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
