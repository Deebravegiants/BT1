This confirms the finding. The gem's own documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (line 125 of `docs/usage/webhooks.md`), and instructs developers to trust `data.shop` — "The shop domain of the webhook" — as an authenticated field (line 14). The gem itself performs the claimed verification via `Utils::HmacValidator.validate(request)` and then hands `request.shop` to the handler, so the binding failure is internal to the gem's own verification step, not a case of the host app ignoring documented guidance.

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, then trusts the `shop` value read from an unauthenticated HTTP header to attribute the payload to a tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the signature [2](#0-1) . `Utils::HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the body) against the app's shared `Context.api_secret_key` [3](#0-2) . `Registry.process` checks only this body HMAC and then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, etc., taken straight from the (unauthenticated) headers [4](#0-3) .

This breaks the identity binding `shop authenticated == shop attributed to the payload`. Because a single Shopify app has one shared `client_secret` (`Context.api_secret_key`) used for every shop that installs it, any unprivileged merchant who installs the public app on their own store legitimately receives webhooks with a valid HMAC signed with that same shared secret. That merchant can capture a body+HMAC pair from a webhook fired for their own shop, then replay the identical body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. The HMAC still validates (it only covers the body), and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the data came from the victim's shop.

### Impact Explanation
This is a cross-tenant identity confusion: an app relying on `data.shop` (as the gem's own documentation instructs developers to do [5](#0-4) ) to select which tenant's records to update will process attacker-supplied (replayed) data under another merchant's identity, since `Registry.process` claims to "verify the request did indeed come from Shopify" [6](#0-5)  without binding the shop.

### Likelihood Explanation
Any user able to install the public app on a shop they control (a normal, unprivileged onboarding action) can obtain valid `(body, hmac)` pairs for their own shop and replay them with a forged `shop-domain` header; no access to `api_secret_key` or the victim's credentials is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed payload used for validation — e.g., validate the HMAC over `raw_body + shop-domain header` combined, or require a per-shop secret/lookup so the `shop` claim is cryptographically bound to the signature — rather than trusting the unauthenticated header for tenant attribution.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H` sent by Shopify (both signed with the app's shared `client_secret`).
2. Replay to the app's webhook endpoint:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim.myshopify.com   <-- forged
x-shopify-webhook-id: <any>
x-shopify-api-version: <any>

B
```
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate` over body `B` only, which matches `H` (still valid, same shared secret), and calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to attribute attacker-controlled order/webhook data to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
