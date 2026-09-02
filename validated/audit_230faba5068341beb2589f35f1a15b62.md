This confirms the vulnerability: the docs explicitly tell app developers `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook" — developers are expected to trust this field as an authenticated tenant identifier, exactly as `Session#shop` is used as a session key elsewhere.

### Title
Webhook `shop-domain` header is trusted as an authenticated tenant identifier but is excluded from HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only authenticates the JSON body bytes [2](#0-1) . The `shop` field, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed material [3](#0-2) . `Registry.process` verifies only the HMAC of the body and then forwards `request.shop` unchecked into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identity [4](#0-3) .

### Finding Description
This is a direct structural analog to the reported bug class: a field that is *acted upon* (the `shop` used to attribute/scope the webhook event) is not covered by the same integrity check (`HMAC`) that is presented as the authentication mechanism for the whole request. The equality that should hold is:

`shop trusted by handler == shop that was cryptographically bound to this exact request`

But the actual binding is:

`HMAC covers raw_body only` ⇏ `shop header is authenticated`

Because `hmac` verification (`OpenSSL.secure_compare` in `HmacValidator.validate_signature`, [2](#0-1) ) checks only `to_signable_string` (the raw body), any attacker who can obtain one valid `(raw_body, hmac)` pair for the shared app `client_secret` — trivially, by installing the app on their own shop and capturing a legitimately delivered webhook — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `Request.new` only checks that the header keys are *present* [5](#0-4) ; it performs no cross-check between the header value and anything cryptographically bound to it. `Registry.process` then dispatches to the handler with the forged `shop` [4](#0-3) , and the gem's own documentation instructs app authors to trust `data.shop` as "The shop domain of the webhook" and to key subsequent per-tenant work (e.g. `shop_domain: data.shop`) off of it [6](#0-5) .

### Impact Explanation
This crosses a tenant boundary: an unprivileged attacker who merely has app access on their own shop (no `client_secret`, no victim access token) can cause the app to process events (or trigger downstream per-shop side effects, session/job scoping, data writes keyed by `shop`) attributing them to a victim shop of the attacker's choosing. This matches the "High — cross-tenant access" bar via credential/identity confusion rooted in an unauthenticated field.

### Likelihood Explanation
Any developer who becomes a merchant of the target app (a normal, unprivileged action) can trigger at least one legitimate webhook delivery to capture a valid `(body, hmac)` pair, since the signing secret (`client_secret`) is shared across all shops using the same app — no privileged access is required.

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) into the signed material, or otherwise cryptographically verify the header against the authenticated body, e.g. by including the shop domain in `to_signable_string`, or by cross-referencing the header value against a previously-recorded relation between `webhook_id`/`topic` and the shop from Shopify's registration/GraphQL API. At minimum, the interface and docs should state explicitly that only the body is HMAC-verified and that `shop` must be independently validated (e.g., against known installed shops) before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook (e.g. `orders/create`) on their own shop and captures the raw POST: `raw_body` and the `x-shopify-hmac-sha256` header — both valid under the app's `client_secret`.
3. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the same app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [5](#0-4) ; `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC, which is unchanged [7](#0-6) .
5. `Registry.process` invokes the app handler with `shop: "victim-shop.myshopify.com"` [4](#0-3) , causing the app to perform tenant-scoped work under the victim's identity despite the attacker never having credentials for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
