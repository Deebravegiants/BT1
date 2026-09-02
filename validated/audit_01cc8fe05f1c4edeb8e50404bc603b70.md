### Title
Webhook Shop/Topic Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw HTTP body, while the `shop` (tenant identity) and `topic` values are read from unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` treats a successful HMAC check as proof that the *entire request*, including `request.shop`, came from Shopify for that shop, and hands `request.shop` to the app's handler as the authenticated tenant identifier. Because the shop domain is never covered by the signature, any party capable of obtaining one valid `(body, HMAC)` pair for the app (e.g., a merchant who installs the app on their own store) can replay that same body/HMAC while substituting an arbitrary `shop-domain` header, causing the app to process the payload under a different (victim) merchant's identity.

### Finding Description
The HMAC is computed exclusively from the raw request body: [1](#0-0) 

The `shop` accessor, by contrast, is taken from an ordinary, unsigned request header: [2](#0-1) 

`HmacValidator.validate` only checks the signed bytes returned by `to_signable_string` against the `hmac` header — it has no knowledge of, and does not bind, `shop` or `topic`: [3](#0-2) 

`Registry.process` raises only if the HMAC fails, then immediately trusts `request.shop` (and `request.topic`) as the authenticated tenant identity when constructing the data passed to the app's handler: [4](#0-3) 

The gem's own documentation reinforces this false guarantee, stating that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is simply "The shop domain of the webhook" — with no caveat that this field is unauthenticated: [5](#0-4) [6](#0-5) 

The broken identity equality is: `authenticated_shop (from HMAC-covered bytes) == request.shop (from X-Shopify-Shop-Domain header)`. The left side does not exist — no shop/tenant value is ever included in the signed bytes — so the equality silently defaults to trusting attacker-controllable header input.

Exploit path: the app's `client_secret` (HMAC key) is identical for every shop that installs the app — it is not shop-scoped. An unprivileged internet user can install the target app on their own (e.g., free development) store, trigger any event to obtain one legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify, then send that identical body and HMAC to the app's public webhook endpoint while replacing the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers with a victim shop's domain. `HmacValidator.validate` still succeeds because only the body is checked, and `Registry.process` dispatches the forged data to the handler labeled with the victim's shop.

### Impact Explanation
Any app built on this gem that uses `data.shop` from `WebhookMetadata` to key per-tenant storage, authorization, or business logic (the exact documented usage pattern) can be made to apply attacker-controlled webhook content under a different merchant's identity. This breaks tenant isolation between merchants of the same app — for example forging `orders/create`, `app/uninstalled`, or the mandatory `shop/redact`/`customers/redact` compliance webhooks against a victim shop, corrupting victim data, triggering false data-deletion/redaction workflows, or injecting attacker-chosen content into a victim's records. This is a cross-tenant access issue, matching the Critical impact category.

### Likelihood Explanation
Likelihood is high for any attacker willing to install the target app once on a shop they control (trivial for public/free apps, and Shopify provides free development stores). No access token, `client_secret`, or privileged account is required — only the ability to receive one legitimate webhook and replay it with a modified, unauthenticated header.

### Recommendation
Bind the shop identity to the signed payload before trusting it: e.g., require the raw JSON body itself to carry the shop domain (many Shopify webhook payloads already include a shop-scoped resource id/domain) and cross-check it against the header, or — more robustly — have `HmacValidator`/`Request#to_signable_string` incorporate the `shop-domain` and `topic` headers into the value that is HMAC-verified (this would require coordinating with Shopify's webhook signing scheme) or require app developers to independently verify that `data.shop` corresponds to a shop that has an active, previously-established session/installation before acting on the payload. At minimum, update `docs/usage/webhooks.md` to stop stating that `Registry.process` verifies the request "did indeed come from Shopify" for fields beyond the raw body, and explicitly warn that `data.shop`/`data.topic` are unauthenticated header values that must be independently validated by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and configures/triggers any registered webhook topic (e.g. `orders/create`), capturing the resulting `raw_body` and `X-Shopify-Hmac-Sha256` header sent by Shopify to the app's webhook endpoint.
2. Attacker sends a new HTTP request to the same app webhook endpoint with:
   - Body: identical `raw_body` captured in step 1.
   - Header `X-Shopify-Hmac-Sha256`: identical value captured in step 1.
   - Header `X-Shopify-Shop-Domain`: replaced with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the request; `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only (`lib/shopify_api/webhooks/request.rb:36-38`) and it matches, since the body was not altered.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) proceeds and invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to process attacker-supplied content as an authenticated event from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
