Based on my investigation, this is confirmed and matches the exact pattern the rules describe: a field acted on but not covered by the HMAC.

### Title
Webhook `shop-domain` header is trusted for tenant attribution despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only authenticates the body bytes, never the `shop` value read from the `shopify-shop-domain` / `x-shopify-shop-domain` header [2](#0-1) . `Registry.process` nonetheless forwards this unauthenticated `request.shop` straight to the host application's handler as the tenant identifier for the event [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop header value == shop the HMAC-signed bytes actually originated from`. It doesn't. `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, which for webhooks is `@raw_body` [4](#0-3) [1](#0-0) . The shop-domain header is completely outside that signed string.

Because a single app-wide `client_secret` (the same `Context.api_secret_key`) signs every webhook for every shop that installs the app, any unprivileged merchant who installs the app on their own store legitimately receives real `(body, hmac)` pairs signed with that shared secret. Nothing in this gem prevents that merchant from replaying the exact same `body`/`hmac` bytes to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` passes the attacker-chosen `shop` value into `WebhookMetadata` unaltered [5](#0-4) . Documentation confirms host apps are expected to key their tenant logic directly off `data.shop` from the handler callback [6](#0-5) .

### Impact Explanation
A host application that (as documented) uses `data.shop` to select which shop's session/records to update when processing webhook data can be tricked into associating one shop's event/body data with another shop's identity, since the gem provides no cryptographic binding between the two. This is a cross-tenant identity-attribution flaw rooted entirely in this gem's `Request`/`HmacValidator`/`Registry` code, not in host-application misuse of an undocumented contract — the documented contract itself (`data.shop`) is unauthenticated.

### Likelihood Explanation
Exploitation only requires being an ordinary merchant who has installed the target app (unprivileged, no `api_secret_key`, no access token needed) and the ability to POST arbitrary HTTP headers/body to the app's public webhook endpoint with a body+HMAC pair they legitimately received for their own store.

### Recommendation
Bind the shop domain into the value that is HMAC-verified — e.g., include the `shop-domain` header (and ideally `topic`/`webhook-id`) inside `to_signable_string`, or independently verify that the shop claimed in the header matches a shop expected for the given webhook subscription/session, before handing `shop` to the handler.

### Proof of Concept
1. App merchant Shop A installs the app and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B` under the shared `api_secret_key`), `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (Shop A's operator) resends the same `B`/`H` to the app's webhook endpoint but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [7](#0-6) .
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and body `B`, which actually originated from Shop A [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
