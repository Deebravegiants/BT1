### Title
Webhook `shop` identity is trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking only the HMAC over the raw body, then hands the handler a `shop` value taken from an HTTP header that is never included in the signed bytes. An attacker who can obtain any one genuinely-signed webhook (e.g. by installing the app on their own store) can replay that exact signed body while swapping the `x-shopify-shop-domain`/`shopify-shop-domain` header to any victim shop, and the forged request will still pass validation.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string` and compares it to the received `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body, `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers that are *not* part of the signed material: [2](#0-1) 

`Registry.process` then trusts `request.shop` (an unauthenticated header) as the tenant identity passed straight to the app's handler: [3](#0-2) 

The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook," encouraging host apps to key their tenant logic (session lookup, job enqueueing, DB writes) directly off `data.shop`: [4](#0-3) [5](#0-4) 

The binding that should hold is: `shop attributed to the payload == shop cryptographically bound to that payload by the signature`. Because `to_signable_string` only covers `@raw_body`, this equality does not hold — the `shop` field is fully attacker-controlled independent of the signed body, exactly analogous to the reported bug class of "a field acted on but not covered by the HMAC."

Since Shopify webhook HMACs are computed with the app's single `client_secret`, shared across *every* shop that installs the app (it is not a per-shop secret), any attacker who installs the app on their own shop can capture a legitimately-signed webhook for their own tenant. They can then replay the identical `raw_body` + `hmac` header pair while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` invokes the handler with `WebhookMetadata` carrying the victim's shop but the attacker's chosen body content.

### Impact Explanation
This breaks the tenant boundary: an unprivileged user (any merchant who has installed the app) can make the gem deliver a payload of their choosing to the handler under another merchant's identity. Because host apps are documented to use `data.shop` to route persistence/session lookups, this enables cross-tenant data injection/confusion — one tenant's forged webhook can be attributed to another tenant, satisfying the "cross-tenant access" Critical impact bucket.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app on a shop they control (the normal, unprivileged path for public/embedded Shopify apps) — no privileged credentials, leaked secrets, or access token theft are required, only a legitimate app installation on an attacker-owned store and the ability to POST a raw HTTP request with custom headers to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) to the HMAC-verified material, e.g. by including the shop header in `to_signable_string`, or by requiring host apps to cross-check `request.shop` against an independently known/authorized shop record before trusting it for tenant routing, rather than treating "HMAC valid" as implying "the accompanying headers are authentic."

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, and triggers any webhook (e.g. `orders/create`) to their own registered endpoint, capturing the raw POST body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed with the app's shared `client_secret`).
2. Attacker sends a new HTTP request to the app's public webhook endpoint with the exact same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object whose `shop` returns `"victim.myshopify.com"` while `hmac`/`to_signable_string` are unaffected by the header change (`lib/shopify_api/webhooks/request.rb` lines 20-38).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` (`lib/shopify_api/webhooks/registry.rb` line 190; `lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker-controlled parsed body> ...)` (`lib/shopify_api/webhooks/registry.rb` lines 198-199), causing the host app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
