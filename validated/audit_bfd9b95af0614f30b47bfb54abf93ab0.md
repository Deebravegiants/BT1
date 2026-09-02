### Title
Webhook HMAC does not bind the `shop` (or `topic`/`webhook-id`) header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body* was signed with the app's secret [2](#0-1) . The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from attacker-controllable HTTP headers [3](#0-2)  and are never included in what the HMAC covers. `Registry.process` trusts `request.shop` unconditionally and hands it to the app's handler as the tenant identifier [4](#0-3) .

### Finding Description
The identity binding that should hold is:

`shop header used to route/attribute the webhook == shop bound by the HMAC signature`

This equality does not hold. `HmacValidator.validate` only checks `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature` is derived solely from `verifiable_query.to_signable_string`, which for `Webhooks::Request` is just `@raw_body` [5](#0-4) [6](#0-5) . The `shop`, `topic`, `webhook_id`, and `api_version` fields come from `shopify_header(...)`, which simply reads from the (attacker-suppliable) headers hash passed into `Request.new` [3](#0-2) [7](#0-6) .

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` without re-checking that these values are actually consistent with anything the signature covers, before dispatching to the app-registered handler [4](#0-3) . The gem's own documentation instructs consuming apps to use `data.shop` directly as the tenant key (e.g. `shop_domain: data.shop`) [8](#0-7) , i.e. the documented API explicitly relies on `request.shop` being trustworthy once `Registry.process` has "verified the request did indeed come from Shopify" [9](#0-8) . That guarantee does not extend to the `shop` field.

Consequently, any party capable of sending an HTTP request to the app's webhook endpoint with a **valid `(body, hmac)` pair for their own shop** can freely change the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers to any value, and `Registry.process` will accept it and pass the attacker-chosen `shop` value on to the handler as if Shopify had generated a webhook for that shop. A merchant who legitimately installs the app receives real Shopify webhooks (correctly signed for their own shop) at the app's public callback URL; they can replay that exact `(body, hmac)` pair while substituting a different shop-domain header to make the app process data under another tenant's identity.

### Impact Explanation
This breaks the shop-authentication boundary the app relies on for multi-tenant webhook processing: it allows cross-tenant confusion/access where webhook data intended to be attributable to shop A can be attributed to shop B purely by header manipulation, without possessing the `client_secret`/`api_secret_key`. Depending on how the host app uses `data.shop` (e.g., looking up a stored session/access token for that shop and acting on it, as the docs suggest), this can lead to cross-tenant data corruption or actions being taken against the wrong merchant's stored session.

### Likelihood Explanation
Exploitation requires an attacker to obtain at least one legitimately-signed `(body, hmac)` pair, which any existing merchant of the app can trivially obtain by simply using the app normally (Shopify will deliver a genuine signed webhook to their installation). No secret key, leaked credentials, or privileged access is required. The endpoint is a normal public HTTP route (`docs/usage/webhooks.md`'s example is a plain unauthenticated controller action), so replaying with modified headers is straightforward for anyone able to send HTTP requests.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` values in the signable payload (or otherwise bind them to the HMAC, e.g. by hashing `raw_body` together with the header values before comparing), so that changing any of these headers invalidates the signature. At minimum, document/enforce that `request.shop` must be cross-checked by the consuming app against a known/expected shop (e.g., the shop tied to the webhook subscription that was registered), rather than treating `Registry.process`'s HMAC check as validating the shop identity too.

### Proof of Concept
1. App merchant "attacker-shop" installs the app; Shopify delivers a legitimate webhook to the app's callback URL:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body B for attacker-shop>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: B
   ```
2. Attacker captures this exact request (trivial, since it's addressed to a URL they control/observe) and resends it to the same endpoint, changing only the header:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B   (unchanged)
   ```
3. `HmacValidator.validate` succeeds because it only checks `body B` against the HMAC [1](#0-0) ; `Registry.process` calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [10](#0-9) , causing the app to process attacker-controlled data under the victim shop's identity.

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
