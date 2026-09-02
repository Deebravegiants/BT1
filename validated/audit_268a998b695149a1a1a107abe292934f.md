### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant/handler routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies the HMAC exclusively over the request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never part of the signed material, yet `Registry.process` uses the unauthenticated `topic` header to select the handler and forwards the unauthenticated `shop` header directly to the host application's handler as the tenant identity.

### Finding Description
`HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body bytes: [2](#0-1) 

Meanwhile, `topic`, `shop`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` only checks the HMAC of the body, then uses the unauthenticated `topic` header to look up the handler and passes the unauthenticated `shop` header to that handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is: `shop that authorized/produced the signed bytes == shop attributed to the webhook data delivered to the handler`. Because the header `shop` is not part of `to_signable_string`, this equality is not enforced by the gem. A party who can obtain one validly-signed `(raw_body, hmac)` pair for the shared `api_secret_key` — trivially achievable by an unprivileged attacker who installs the app on their own (attacker-controlled) development shop and captures the resulting legitimate webhook — can replay that same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic` header). `HmacValidator.validate` will still return `true` because it only re-derives the signature from `raw_body`, and `Registry.process` will dispatch the (attacker-chosen) topic/handler with `WebhookMetadata#shop` set to whatever domain the attacker supplied — not the shop that actually produced/signed the payload.

### Impact Explanation
This breaks the tenant-identity binding that `Registry.process` relies on to route webhook data to the correct merchant's data store. A host application built on this gem's documented API — trusting `WebhookMetadata#shop` because the request "passed HMAC validation" — can be made to process attacker-supplied webhook content while believing it is scoped to a shop the attacker does not control (cross-tenant data injection/confusion). This matches the Critical "cross-tenant access" category: an unprivileged actor with only their own legitimately-signed webhook traffic can cause the host app to attribute forged data to a victim tenant, entirely through this gem's own verification/dispatch logic (`HmacValidator` + `Webhooks::Registry#process`), without needing the app's `api_secret_key`, an access token, or any privileged credential.

### Likelihood Explanation
Likelihood is High: any developer or merchant can install a Shopify app on a free development store, trigger events to receive genuinely signed webhooks for topics they choose, capture the raw body + `X-Shopify-Hmac-Sha256` value, and replay them to the same public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. No secret material, TLS interception, or social engineering is required — only network access to the app's public webhook URL, which by design must be internet-reachable.

### Recommendation
Bind the identity-carrying headers to the signed material before trusting them in `Registry.process`:
- Include `shop-domain` (and ideally `topic`, `webhook-id`) in the bytes that are HMAC-verified, or
- Require the host application to independently correlate `request.shop` against a shop it has a stored/active session for before invoking the handler, and document this requirement clearly, or
- At minimum, have `Webhooks::Request`/`Registry` treat `shop` as untrusted metadata unless additionally corroborated (e.g., cross-checked against an existing installed-shop record) rather than passing it straight into `WebhookMetadata` as an authenticated field.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers an event (e.g., `orders/create`) to receive a real webhook signed with the app's shared `api_secret_key`. They capture:
   - `raw_body` = `{"id":1,...}`
   - `X-Shopify-Hmac-Sha256` = `<valid hmac of raw_body>`
2. Attacker sends a POST to the host app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any topic registered by the app)
3. The gem builds `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and calls `Utils::HmacValidator.validate(request)`. Since `to_signable_string` is only `raw_body`, validation succeeds: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: request.parsed_body, ...)`, causing the host app to process attacker-controlled data as if it originated from `victim.myshopify.com`: [6](#0-5)

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
