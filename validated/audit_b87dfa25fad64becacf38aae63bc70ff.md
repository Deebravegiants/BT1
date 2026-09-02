This confirms the finding: the docs explicitly present `data.shop` as a trusted field derived from the webhook request, and `ShopifyAPI::Webhooks::Registry.process` documentation says it "will verify the request did indeed come from Shopify" — but the verification (`Utils::HmacValidator.validate(request)`) only authenticates `request.to_signable_string`, which is `@raw_body` alone. The `shop` field is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header and flows into `WebhookMetadata.shop` without ever being covered by the HMAC or cross-checked against anything.

### Title
Webhook `shop` field is not covered by HMAC verification, allowing shop-identity forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw request body against the HMAC signature, but hands the caller's handler a `shop` value that is taken from an attacker-controllable header and is never part of the signed data. This breaks the identity binding `shop_authenticated_by_hmac == shop_delivered_to_handler`, letting anyone who can produce one validly-signed webhook body (the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, not per-tenant) relabel that payload as coming from an arbitrary other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
so the only bytes ever authenticated are `@raw_body`. Meanwhile `shop` is read directly from the unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC over that same signable string and then immediately forwards the unauthenticated `request.shop` value into the handler: [3](#0-2) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and constant-time compares it to the header HMAC — but `to_signable_string` never includes the shop domain: [4](#0-3) 

The gem's own documentation instructs developers to trust `data.shop` from the handler as "The shop domain of the webhook" and states that `process` "will verify the request did indeed come from Shopify," implying the shop identity itself is authenticated: [5](#0-4)  and [6](#0-5) 

Because the `api_secret_key`/`client_secret` used to sign webhooks is one value per app (shared by every shop that installs that app), any merchant who legitimately installed the app and received one genuine webhook (with a correctly computed HMAC over `raw_body`) can capture that `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain`/`shopify-shop-domain` header value pointing at a victim shop. `HmacValidator.validate` will still pass because it only checks the body/HMAC pair, and `WebhookMetadata.shop` will contain the attacker-chosen victim shop domain, which the handler is documented to trust for tenant-scoped side effects (e.g. `shop_domain: data.shop` in the docs example).

### Impact Explanation
This is a cross-tenant identity confusion: the field the host application is told (by this gem's own docs and API surface) to treat as the authenticated tenant identifier for a webhook is not bound to the cryptographic verification that authenticates the message. Any app built following this gem's documented pattern (using `data.shop` to route/attribute the webhook body to a shop record) is exposed to processing another shop's data under an attacker-chosen tenant, i.e., cross-tenant access.

### Likelihood Explanation
Exploitation requires only that the attacker be a shop that has installed the target app (to receive one genuinely signed webhook body/HMAC pair for some topic) and be able to send an HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header and the captured body+HMAC — no access token, `api_secret_key`, or privileged credentials are needed, satisfying the unprivileged-internet-user bar.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or independently verify `request.shop` against a known-installed-shop list keyed by the delivering webhook subscription/session before trusting it in `WebhookMetadata`, so the value handed to `WebhookHandler#handle` is bound to the same bytes that were HMAC-authenticated.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger a webhook (e.g., `orders/create`) and capture the raw POST: `raw_body` and header `x-shopify-hmac-sha256` (a valid HMAC-SHA256 of `raw_body` under the app's shared `api_secret_key`).
2. Replay this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook route, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [4](#0-3)  — validation succeeds because `raw_body`/HMAC pair is genuinely valid.
4. `handler.handle` receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own order payload>, ...)` [7](#0-6) , so the app's tenant-scoped logic (e.g. `perform_later(shop_domain: data.shop, webhook: data.body)` as shown in the gem's own doc example) now processes attacker-supplied data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
