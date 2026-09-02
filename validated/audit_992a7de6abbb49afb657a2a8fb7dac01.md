Confirmed: `Registry.process` at `lib/shopify_api/webhooks/registry.rb:188-200` only validates `Utils::HmacValidator.validate(request)` and then dispatches based on `request.topic`, passing `request.shop`, `request.webhook_id`, and `request.api_version` straight into `WebhookMetadata` for the handler — none of these are covered by the HMAC. `Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38` returns only `@raw_body`, and `Request#shop`/`#topic`/`#webhook_id`/`#api_version` at lines 15-33 are read verbatim from attacker-controllable HTTP headers. Yet `docs/usage/webhooks.md:125` documents that calling `Registry.process` "will verify the request did indeed come from Shopify," which overstates the guarantee: only the body bytes are authenticated, not the shop/topic identity bound to them.

### Title
Webhook shop/topic identity headers are not covered by the HMAC verified in `Registry.process` - (File: lib/shopify_api/webhooks/registry.rb, lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate` succeeds, but that validation only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — read from `X-Shopify-*` headers — are never part of the signed content, yet they are trusted as the tenant/routing identity handed to the app's handler.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from headers with no cryptographic binding to the HMAC [2](#0-1) .

`Registry.process` validates only the HMAC and then uses the unauthenticated `request.topic` to select a handler and forwards the unauthenticated `request.shop` into `WebhookMetadata` passed to the handler [3](#0-2) . The equality the code implicitly assumes — "shop header used for tenant identification == shop that produced the signed body" — is never checked; only "HMAC(secret, body) == received HMAC" is checked.

Because the same `api_secret_key` signs webhooks for every shop that installs the app, any legitimate webhook body a merchant (including an attacker who installs their own copy of the app) has received carries a valid HMAC regardless of which shop it was originally destined for. An attacker who controls their own store's webhook delivery (or captures one delivery) can resend the exact `raw_body`/HMAC pair to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) with a victim shop's values, since none of those headers affect the HMAC check.

### Impact Explanation
This breaks the identity binding between "the request Shopify verified" and "the tenant record the host application acts on," enabling cross-tenant data injection: the handler executes with `data.shop` set to an arbitrary attacker-chosen shop domain while `data.body` is attacker-controlled content that legitimately passed HMAC verification. Typical handler implementations use `data.shop` to look up/update the merchant's local session or record store, so this can lead to writing or acting on data under a victim shop's identity. This falls under the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimately-signed webhook body (trivially obtainable by installing the app on their own store, since app webhooks use the single shared `api_secret_key`) and the ability to send an HTTP request to the app's public webhook endpoint with custom headers — both are unprivileged-internet-user actions with no access token, `client_secret`, or leaked credentials required. The gem's own documentation increases likelihood of unsafe reliance by asserting `Registry.process` "will verify the request did indeed come from Shopify" without qualifying that this covers the body only [4](#0-3) .

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content, or otherwise cryptographically bind them (e.g., compute a combined digest over headers+body) before trusting `request.shop`/`request.topic` in `Registry.process`. At minimum, document prominently that `Registry.process` only authenticates the body and that host applications must independently verify `data.shop` against a known/installed shop before using it as a tenant key.

### Proof of Concept
1. Install the target app on an attacker-owned store; trigger a webhook (e.g. `orders/create`) to capture a valid `raw_body` and its `X-Shopify-Hmac-Sha256` value from Shopify.
2. Replay that exact `raw_body` + `X-Shopify-Hmac-Sha256` to the app's public webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC [5](#0-4) .
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's `body`, despite the request never having been produced or signed for that shop.

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
