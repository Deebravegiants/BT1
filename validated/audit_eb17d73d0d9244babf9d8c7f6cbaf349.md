Confirmed: the docs explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" as a whole, and that `data.shop` is "The shop domain of the webhook" — implying the entire tuple (topic, shop, body) is authenticated together. In reality, only the raw body bytes are covered by the HMAC.

### Title
Webhook shop-domain header is not covered by HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then reads the tenant identity (`shop`) from an HTTP header that is never included in the signed material. Any party that can obtain one genuine HMAC-signed webhook body (e.g., a self-serve merchant who installs the app on their own store) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value, and the gem will accept it as an authentic webhook "from" the spoofed shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field via `OpenSSL.secure_compare` [1](#0-0) . For webhook requests, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all derived from separate, unsigned HTTP headers [2](#0-1) .

`Registry.process` performs exactly one authenticity check — `Utils::HmacValidator.validate(request)` — and then unconditionally trusts `request.shop`, `request.topic`, etc. to build the `WebhookMetadata` passed to the app's handler [3](#0-2) .

The binding that is broken (expressed as an equality that should hold but doesn't):
`shop asserted by the header == shop that produced the HMAC-signed body`

The HMAC only proves "this body byte string was produced with the app's shared `client_secret`" — it says nothing about which shop header should accompany it. Because Shopify uses the same `client_secret` to sign webhooks for every shop that installs the app, an attacker who controls one shop (trivially available for any public/self-serve app) can capture a legitimately-signed `(raw_body, hmac)` pair from their own store's webhook deliveries, then POST that exact byte-for-byte body and HMAC to the app's webhook endpoint with the `shop-domain` header changed to any victim shop domain string. `HmacValidator.validate` will still return `true` because it only checks the body against the secret, never checking that the header-derived `shop` was part of the signed content.

### Impact Explanation
This breaks the tenant-isolation boundary the gem's webhook processing pipeline is documented to provide. The docs describe `data.shop` as "The shop domain of the webhook" and state that `Registry.process` "will verify the request did indeed come from Shopify" [4](#0-3) [5](#0-4) , implying the whole tuple is authenticated as a unit — but only the body is. Applications built on this gem's documented contract (using `data.shop` to route/attribute webhook data to a tenant record, as shown in the gem's own example handler [6](#0-5) ) will attribute attacker-chosen body content to an arbitrary victim shop of the attacker's choosing, i.e., cross-tenant data injection. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to be able to install the target app on a store they control (common for self-serve/public Shopify apps) and to know/guess a victim shop's `myshopify.com` domain (often discoverable or guessable), then replay a captured body+HMAC pair with a modified header via a simple HTTP request. No access to `client_secret`, access tokens, or any privileged credential is required beyond ordinary app installation.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signed payload verification — i.e., include them in `to_signable_string`, or otherwise cryptographically bind the header set to the body so a captured signature cannot be replayed against a different shop/topic pair. At minimum, document that `Registry.process` does not authenticate the `shop` header, so consuming applications cannot mistakenly treat `data.shop` as verified.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify delivers a webhook to the app with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker captures `(B, H)` (e.g., via a proxy on their own infra, or from server logs they control).
4. Attacker sends a new HTTP POST to the app's webhook endpoint with the same raw body `B`, the same `x-shopify-hmac-sha256: H` header, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` [7](#0-6) .
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [8](#0-7) , causing the app to process attacker-controlled data as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
