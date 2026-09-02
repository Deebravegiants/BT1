This confirms the finding: the gem's own documentation (`docs/usage/webhooks.md`) explicitly tells host apps to trust `data.shop` as "The shop domain of the webhook" and to key their per-tenant work off it (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`). This is the gem's documented API contract, not an app-side misuse, so the finding is in scope.

### Title
Webhook `shop` (and topic/api_version/webhook_id) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC validation, while the tenant-identifying `shop` field (along with `topic`, `webhook_id`, `api_version`) is read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body HMAC matches, then constructs `WebhookMetadata` using the header-derived `shop`, which the host app is instructed by this gem's own docs to trust as the tenant key.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` header — since `to_signable_string` is body-only, the signature says nothing about which headers accompanied that body: [3](#0-2) 

`Registry.process` only checks this body HMAC, then builds `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` — none of which were part of the verified signature — and hands it to the app's handler as trusted: [4](#0-3) 

The gem's documentation instructs integrators to treat `data.shop` as the authoritative tenant identifier for dispatching webhook work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), i.e. the gem's documented contract is that `HmacValidator.validate(request) == true` implies `request.shop` is the shop that actually sent the webhook. That equality does not hold: an attacker holding one valid `(raw_body, hmac)` pair for their own shop (they legitimately receive real webhooks for their own installed app) can replay the identical body/HMAC to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header value. `Utils::HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` will dispatch to the handler with the attacker-chosen `shop` value instead of the true origin shop.

### Impact Explanation
This breaks the identity binding "the shop asserted by a verified webhook equals the shop that actually generated it," letting an authenticated-but-unprivileged attacker (any merchant with the app installed, who naturally receives valid signed webhook bodies for their own shop) inject data under an arbitrary victim shop domain into the host app's per-tenant processing pipeline, since the app is following this gem's documented pattern of keying tenant work off `data.shop`. This is a cross-tenant identity/data confusion issue reachable purely through the gem's public `Webhooks::Request`/`Registry.process` API, with no access token, `client_secret`, or privileged account required.

### Likelihood Explanation
Any party who can get one legitimate webhook delivered to their own app instance (trivial — install the app on a shop they control, or observe a webhook they legitimately receive) has a valid `(body, hmac)` pair. Replaying it with a modified `shop` header requires only the ability to send an HTTP POST to the app's public webhook endpoint — no secret material, TLS interception, or social engineering needed.

### Recommendation
Bind the tenant-identifying headers into the signed material verified against `hmac`, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the signature (e.g., by including them in `to_signable_string`, or by requiring the host app to additionally verify `shop` against session/install records before trusting `WebhookMetadata#shop`). At minimum, update the gem's documentation to explicitly warn that `data.shop` is not covered by the HMAC and must not be treated as authenticated without additional verification against the app's own shop/install registry.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook POST with body `{"id":1}` and header `x-shopify-hmac-sha256: <valid-hmac-of-body>` (computed by Shopify using the app's real `client_secret`, unknown to the attacker but delivered on the wire).
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `shop = "victim-shop.myshopify.com"`, `hmac` unchanged.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only — unaffected by the header change — and returns `true`.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and calls the app's handler, which (per this gem's documented usage) processes the body as belonging to `victim-shop.myshopify.com`, despite the payload never having been produced for that shop. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
