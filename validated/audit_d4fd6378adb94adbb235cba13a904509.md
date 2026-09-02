### Title
Webhook HMAC verification does not bind the `shop` (or `topic`/`webhook_id`) header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields are taken verbatim from unauthenticated HTTP headers and passed straight through to the app's webhook handler as trusted identity data. `ShopifyAPI::Webhooks::Registry.process` treats a passing HMAC check as proof that "the request did indeed come from Shopify" for that specific shop, but the signature never actually binds the shop to the payload.

### Finding Description
In `Request#to_signable_string`, only `@raw_body` is returned as the signable content: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers that are never included in the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` gates on this HMAC check and then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — as the tenant identity handed to the app's handler: [4](#0-3) 

Because the HMAC secret (`api_secret_key`/`client_secret`) is the same across every shop that has installed the app, any attacker who controls a shop that has the app installed can capture a legitimately-signed webhook body+signature for their own shop, then replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to a different, victim shop that also has the app installed. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will dispatch the handler with `data.shop` set to the victim shop. The gem's own documentation confirms host apps are expected to trust `data.shop` as the "shop domain of the webhook" and use it to route/attribute per-tenant work: [5](#0-4) [6](#0-5) 

This is the same class of bug as the referenced report: a field the application acts on (`shop`) is not covered by the integrity check (`HMAC` over `raw_body` only) that is supposed to authenticate the whole message, so state that should only be reachable for one identity can be attributed to another.

### Impact Explanation
This breaks the tenant-binding invariant `shop_that_authenticated_the_request == shop_attributed_to_the_payload`. A host application that follows the gem's documented pattern (using `data.shop` to key per-shop side effects, e.g., updating shop-scoped records, enqueuing shop-scoped jobs) can be made to apply attacker-controlled webhook body content under a different, victim shop's identity — a cross-tenant data confusion/injection primitive reachable by any unprivileged internet user who runs the app on their own shop.

### Likelihood Explanation
Exploitation requires only that the attacker (1) installs the target app on their own shop (a normal, unprivileged action for any public app) to receive a validly-signed webhook, and (2) can send arbitrary HTTP requests with custom headers to the app's public webhook endpoint (the endpoint is public by design). No credentials, tokens, or elevated access are needed beyond what any merchant installing the app already has.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`) in the signed/verified material, or otherwise cryptographically bind the shop domain to the payload before it is trusted, e.g. by cross-checking `request.shop` against a shop the app has an active, previously-registered webhook subscription for and rejecting mismatches. At minimum, update `Request#to_signable_string` / `HmacValidator` so the HMAC check covers the full set of Shopify-controlled headers that downstream code relies on, and adjust the docs so `Registry.process` is not described as proof that the request "did indeed come from Shopify" for a specific shop when only the body is verified.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com`, triggering a real webhook (e.g. `orders/create`) signed by Shopify with the app's shared `client_secret`.
2. Attacker captures the raw body and the `x-shopify-hmac-sha256` value from that legitimate request.
3. Attacker replays an HTTP POST to the app's webhook endpoint with the same body/HMAC but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com` (a shop that also has the app installed).
4. `ShopifyAPI::Webhooks::Request.new` parses this into `shop = "victim-shop.myshopify.com"`; `Utils::HmacValidator.validate` still returns `true` because it only checks `raw_body` against the secret.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
