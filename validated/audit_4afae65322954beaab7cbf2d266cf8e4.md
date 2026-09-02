### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC check only authenticates the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values — all read from unauthenticated HTTP headers — are handed to the app's webhook handler as trusted identity data, even though they are never part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers, completely outside the signed payload: [2](#0-1) 

`Registry.process` verifies the HMAC and then trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The HMAC computation itself only signs the body string with the secret: [4](#0-3) 

The identity binding that should hold is: `bytes_verified_by_hmac == bytes_the_handler_acts_on`. In fact `bytes_verified_by_hmac = raw_body` while `bytes_the_handler_acts_on = {raw_body, shop-domain header, topic header, webhook-id header, api-version header}`. Because the header set is outside the HMAC, anyone who obtains one legitimately-signed webhook delivery (e.g., a merchant/developer who owns a store subscribed to the app, an unprivileged actor with respect to other tenants) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different tenant's shop domain (and/or a different topic/webhook-id). The signature still validates because it is computed solely over the untouched body, yet the handler receives fabricated tenant/topic identity via `WebhookMetadata.shop` / `.topic`.

The docs explicitly promise more than the code delivers: [5](#0-4) 
and describe `shop` as trustworthy webhook metadata for the handler to act on: [6](#0-5) 

This is not a case of the host application ignoring documented behavior — the documentation itself asserts the request's Shopify origin is verified and presents `shop` as reliable data, when the gem's own `process` method does not bind that field to the cryptographic check it performs.

### Impact Explanation
An attacker who can obtain any single valid webhook delivery for one tenant (trivial for a developer building/testing an app that receives webhooks for their own store, or any merchant using the app) can forge the `shop-domain` header to impersonate a different, victim tenant while keeping a fully valid signature. If the host application's webhook handler uses `data.shop` to attribute the (attacker's own, but now mislabeled) webhook payload to another store — e.g., writing to that store's records, triggering per-tenant business logic, or looking up/using that store's stored access token — this results in cross-tenant data confusion driven entirely by a gap in this gem's own verification method, not a documented, opt-in application behavior. This falls in the cross-tenant access impact category.

### Likelihood Explanation
Likelihood is moderate: the attacker must first obtain one legitimately-signed webhook body (achievable simply by being an app user/merchant with their own store subscribed to the app, or by intercepting one delivery), then can freely resend it to the same public endpoint with modified identity headers, since nothing beyond the raw body is checked. No knowledge of `client_secret` or access tokens is required.

### Recommendation
Bind the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the value that is HMAC-verified — e.g., include them (or a canonicalized combination of them with the body) in `to_signable_string`, or otherwise validate `shop`/`topic` against an out-of-band trusted source (such as a shop already known to have valid registration for that topic) before constructing `WebhookMetadata`. At minimum, update the documentation to clarify that only the body is authenticated and that header-derived fields (`shop`, `topic`, `webhook_id`, `api_version`) require independent validation by the consuming application before being trusted for tenant-scoped actions.

### Proof of Concept
1. App subscribes to a webhook topic and stands up a controller per `docs/usage/webhooks.md`:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
)
```
2. Attacker (owner of `attacker-shop.myshopify.com`, a store legitimately subscribed to the app) triggers a real event and captures the genuine webhook POST, including a valid `X-Shopify-Hmac-Sha256` header computed over the raw body:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid-signature-for-body>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
Body: {"id":1,...}
```
3. Attacker resends the identical body and HMAC header to the same endpoint but swaps the shop header:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same-valid-signature-for-same-body>
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Body: {"id":1,...}   # unchanged
```
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks the untouched body/signature pair, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches to the handler with `shop: "victim-shop.myshopify.com"`, even though the event has nothing to do with that tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
