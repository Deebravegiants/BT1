### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts an unauthenticated header field (`shop-domain`) as the tenant identity passed to the app's handler. This breaks the equality `shop authenticated by HMAC == shop delivered to handler as WebhookMetadata#shop`, the exact class of binding failure called out in the analog rules (a field acted on but not covered by the HMAC).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed content at all: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e. the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` validates that HMAC and, once it passes, unconditionally forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The gem's own documentation instructs handler authors to trust `data.shop` as "The shop domain of the webhook" and use it to route/attribute work per-tenant: [6](#0-5) 

Contrast this with the OAuth callback path in the same gem, where the analogous `shop` field is explicitly included in the signable string and therefore is bound to the HMAC: [7](#0-6) 

That difference confirms the webhook code path is missing the same binding the OAuth path enforces: the identity field (`shop`) that the handler acts on is never covered by the signature that authenticates the request.

### Impact Explanation
An unprivileged internet user who can install the target app on any shop (e.g. their own free/dev store) can receive a genuine webhook with a valid `(raw_body, hmac)` pair signed by the app's shared secret. Because the HMAC never binds `shop-domain`, that same `(raw_body, hmac)` pair remains valid if replayed to the app's public webhook endpoint with the `shop-domain` header changed to an arbitrary victim shop. `Registry.process` will accept the forged request (HMAC check passes) and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. Any handler that uses `data.shop` to look up/act on tenant-scoped state (per the gem's documented usage pattern) can be tricked into attributing or acting on data under a shop it was never actually sent by. This is a cross-tenant identity-binding failure reachable by any user who can obtain one valid signed webhook (their own store is sufficient) and send arbitrary HTTP requests to the app's public webhook callback route — no credentials, TLS interception, or privileged access required.

### Likelihood Explanation
Likelihood is significant: obtaining a valid `(body, hmac)` pair requires only installing the app on an attacker-controlled store (a normal, unprivileged action for any public/multi-tenant app), and the webhook callback endpoint is by design a public, unauthenticated HTTP route. No secret material needs to be extracted; the gem's own body-only signing scheme is the root cause.

### Recommendation
Bind the shop to the authenticated payload before trusting it: verify that `request.shop` matches the shop of a genuinely-established session/installation known to the app (rather than trusting the header at face value), or extend the signable content used for verification to include the shop domain when computing/comparing the HMAC, mirroring how `AuthQuery#to_signable_string` explicitly incorporates `shop`. At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must be independently cross-checked by the host application against known installed shops before being used for tenant-scoped actions.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger an event (e.g. `orders/create`) to receive a genuine webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(B, secret)`.
2. Capture `B` and the HMAC value.
3. Send a forged POST to the app's public webhook callback route with:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Hmac-Sha256: <captured HMAC>` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (attacker-modified)
   - Body: `B` (unchanged)
4. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC via `Utils::HmacValidator.validate`, which succeeds because it only checks `B` against the HMAC — the `shop-domain` header is never part of the signed content.
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to process/attribute data as if it originated from `victim-shop.myshopify.com`, even though that shop never sent this webhook.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L12-27)
```markdown
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
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
