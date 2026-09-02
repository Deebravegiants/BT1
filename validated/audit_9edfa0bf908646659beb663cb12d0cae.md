### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before handing the webhook to the app's handler. In reality, the HMAC signature only authenticates the raw JSON body; the `shop` value passed to the handler is read from an unauthenticated HTTP header and is never covered by that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`Request#shop`, however, is parsed straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then forwards `request.shop` (the unverified header) directly into `WebhookMetadata` as the tenant identifier passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute the signature over `verifiable_query.to_signable_string` (i.e., the body) with the app's shared `api_secret_key`: [4](#0-3) 

Because `api_secret_key` is a single, app-wide secret shared across every shop that installs the app (not a per-shop secret), the HMAC only proves "this body was genuinely produced by Shopify for *some* installation of this app" — it does not bind that body to the specific shop that generated it. The identity binding that should hold is:

`shop authenticated by HMAC == shop used as the tenant/session key handed to the app handler`

but here the left side is never computed at all — the `shop` field is not in the HMAC payload, so the equality can be broken trivially.

The documentation reinforces the false guarantee, describing `shop` as an authenticated attribute of "the webhook" once `process` has "verified the request did indeed come from Shopify": [5](#0-4) [6](#0-5) 

### Impact Explanation
Any user who can install the app on their own store (an unprivileged action any merchant can take) can capture a genuine, validly-HMAC'd webhook body for their own shop (e.g., from `orders/create`), then replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Registry.process` will pass HMAC validation (the body's signature is unchanged and still valid under the shared `api_secret_key`) and will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop. If the host application uses `data.shop` as the tenant key to look up sessions, write records, or trigger downstream actions (as the library's own documentation example does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this results in cross-tenant data injection/confusion — the library's contract, not just host misuse, is at fault because it exposes an unauthenticated field as if it were verified.

### Likelihood Explanation
High likelihood for any multi-tenant Shopify app: obtaining a legitimately-signed webhook payload requires only installing the app on an attacker-owned development/test store (no special privileges), and the webhook endpoint is a public HTTP endpoint reachable by anyone who can craft the correct headers.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or independently verify that `request.shop` corresponds to a store that has an active, registered session/subscription for that specific webhook id/topic before invoking the handler. At minimum, update the documentation to make clear that `WebhookMetadata#shop` is not authenticated by the HMAC check and must be independently validated by the host app.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger `orders/create` to receive a legitimate webhook `POST` with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
2. Replay the exact same request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` recomputes the HMAC only over `B`, finds it valid (since `H` was computed over `B` with the same shared `api_secret_key`), per `Utils::HmacValidator.validate` at `lib/shopify_api/utils/hmac_validator.rb:13-22`.
4. The handler receives `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's data>, ...)`, from `lib/shopify_api/webhooks/registry.rb:198-199`, causing the host app to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
