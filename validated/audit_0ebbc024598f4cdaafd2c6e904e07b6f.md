### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw HTTP body only, while the shop identity (`x-shopify-shop-domain`), topic, webhook id, and API version are read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then dispatches `request.shop` to the app's handler without ever verifying that the shop claiming to have sent the webhook is actually the shop whose data is contained in the signed body.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` value provided by the caller. [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that play no part in the signed payload: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., that the body byte-for-byte matches the app's secret key) and then immediately hands `request.shop` to the developer's handler as the trusted tenant identifier, with no cross-check that this shop is the one that actually owns/produced the body: [4](#0-3) 

This breaks the identity binding that should hold: `shop authenticated by the HMAC-signed payload == shop used to route/attribute the webhook data`. In reality the equation is `shop verified (none) != shop consumed (attacker-controlled header)`. Because a single `api_secret_key` is shared by the app across **all** installed shops (it is not shop-specific), any merchant who installs the app can:
1. Trigger a genuine webhook delivery from their own store (a legitimate, unprivileged action — anyone can install a public app and trigger, e.g., a `products/create` event).
2. Capture the resulting HTTP POST — a valid `raw_body` + `x-shopify-hmac-sha256` pair signed with the app's secret.
3. Replay that exact body/HMAC pair to the app's public webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to a different, victim shop's domain.

The HMAC still validates (it only covers the body, which is unmodified), so `Registry.process` accepts the request and calls the handler with `shop: <victim's domain>`, `body: <attacker's own webhook data>`.

### Impact Explanation
This lets one tenant of a multi-tenant Shopify app inject arbitrary webhook data (of a type/shape they can produce from their own store) that the host application will attribute to a different shop it has never interacted with in that way, since `request.shop`/`request.topic` are not bound to the signed body. Depending on how the host app's handler uses `shop` (e.g., to look up the shop's session/access token, update per-shop records, or trigger per-shop side effects), this is a cross-tenant data-integrity/access issue — the report's analog to "locking CVX on behalf of VotiumStrategy": an action is credited to (locked/attributed to) an identity that never authorized it, because the identity field is not covered by the integrity check.

### Likelihood Explanation
Any user able to install the app on a store they control (typical for public Shopify apps) can generate valid HMAC-signed webhook bodies and has full control over which unauthenticated header values accompany a replayed request. No access to `api_secret_key`, tokens, or victim credentials is required — only a normal, unprivileged app installation and the ability to POST to the app's publicly documented webhook route.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the HMAC-signed material, or independently verify that the `x-shopify-shop-domain` header corresponds to a shop session/installation the app actually manages before trusting it, rather than deriving tenant identity purely from an unauthenticated header.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and configures the app's webhook endpoint as usual.
2. Attacker triggers `products/create` (or any subscribed topic) on their own store, capturing the raw POST: headers `x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and body `B`.
3. Attacker resends the identical body `B` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) validates the HMAC — it succeeds because the body is unmodified — and calls the handler with `shop: "victim-shop.myshopify.com"`, causing the host app to process attacker-controlled data as if it belonged to the victim shop.

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
