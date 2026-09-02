This confirms the vulnerability path. The gem's documented webhook API instructs developers to trust `data.shop` for tenant identification (as shown in `docs/usage/webhooks.md:14` and the example handler that dispatches jobs keyed by `data.shop`), yet the HMAC signature only binds the raw body.### Title
Webhook `shop-domain` header (and `topic`/`webhook_id`) is not covered by the HMAC, allowing tenant-spoofing of webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC of the raw HTTP body, then hands the caller-supplied `shop-domain`, `topic`, and `webhook_id` headers straight through to the app's handler as trusted tenant-identifying metadata. Because the HMAC signature never covers these headers, any party capable of producing one valid `(body, hmac)` pair for the shared `api_secret_key` (e.g. a merchant who has installed the app on their own store and can capture a real webhook delivery) can resend that exact body/HMAC pair while substituting an arbitrary `shop-domain` header. The gem will report the request as valid and dispatch it to the handler as if it originated from the spoofed shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose contract requires only `hmac` and `to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns **only** the raw body: [2](#0-1) 

Meanwhile, `topic`, `shop`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the signed payload: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header using constant-time comparison — again, this only proves the *body* bytes are authentic, not the headers: [4](#0-3) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop` (and `topic`/`webhook_id`) for dispatch to the app's handler: [5](#0-4) 

This is exactly the identity-binding break described in the report's bug class: "a field acted on but not covered by the HMAC." Here, the `shop` field is *acted on* (used by the host app to attribute the payload to a tenant) but is *not covered by* the HMAC that the gem uses to authenticate the request. The equality that should hold — `shop-domain (authenticated by HMAC) == shop-domain (used for tenant dispatch)` — does not hold, because the HMAC only authenticates the body.

The gem's own documentation instructs developers to treat `data.shop` as the trusted tenant identifier and dispatch tenant-scoped work using it directly, so this is not a case of the host ignoring the gem's documented API — it is following it as instructed: [6](#0-5) 

Since Shopify apps use a single, shared `api_secret_key` (client secret) across *all* installed shops, any user who installs the app on their own store can obtain a validly-HMAC'd webhook body/signature pair (from their own store's real webhook delivery) and then replay that exact body+HMAC to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` header to a victim shop's domain. `HmacValidator.validate` will still pass, because it only checks the body against the shared secret — it has no notion of which shop the signature "belongs to." The app then processes attacker-controlled body content under the victim's tenant/shop identity.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook ingestion: an attacker-controlled shop can inject a payload (with attacker-chosen JSON body content) that is delivered to the host application labeled as belonging to a different (victim) shop. Depending on how the host app uses `data.shop`/`data.body` (e.g., updating orders/customers/inventory records, enqueueing jobs scoped to `shop_domain`), this can result in cross-tenant data corruption/injection — data intended for shop A ends up written into shop B's tenant space. This matches the "cross-tenant access" Critical impact category, since the tenant/session-key binding (`shop`) that downstream code relies on is not actually authenticated by the security mechanism (`HmacValidator`) that gates webhook processing.

### Likelihood Explanation
The prerequisite is modest: the attacker needs to be a legitimate (even free/trial) installer of the target app on their own shop, which is a normal, unprivileged path available to any internet user for a public Shopify app. From there they can capture one real webhook delivery (body + `X-Shopify-Hmac-Sha256`) for a subscribed topic and simply retransmit the identical body/HMAC to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header (and optionally forged `topic`/`webhook_id`, which are equally unauthenticated). No secret material beyond what the attacker already legitimately possesses (their own valid webhook deliveries) is required, and no rate limiting or per-shop signature binding exists in this gem to prevent it.

### Recommendation
Bind the tenant-identifying headers to the authenticated payload before trusting them:
- Include `shop-domain` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or
- Cross-check the `shop-domain` header against the app's installation record for that shop (i.e., verify the request's `Authorization`/session context matches a real installed session for that shop) before dispatching, rather than trusting the header purely because the body's HMAC validates, or
- At minimum, document/clearly warn that `data.shop`/`topic`/`webhook_id` are not cryptographically bound to the HMAC and must not be used as a sole tenant-authentication mechanism, and provide an API to correlate them with a verified installation.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, subscribing to `orders/create`.
2. Shopify delivers a real webhook to the app with a body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this is the same `api_secret_key` shared by all shops using the app.
3. Attacker crafts `B` to contain attacker-chosen JSON content relevant to the target topic (e.g., order details) prior to receiving the real webhook, if the topic content is attacker-influenced (e.g., by creating an order on their own store with attacker-chosen field values), then captures `(B, H)`.
4. Attacker sends a raw HTTP POST to the app's public webhook endpoint with:
   - Body: `B` (unmodified)
   - Header `X-Shopify-Hmac-Sha256: H` (unmodified)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - Header `X-Shopify-Topic: orders/create` (unmodified/forged)
5. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) and `HmacValidator.validate` succeeds, because it only checks `HMAC(api_secret_key, B) == H`, per: [7](#0-6) 
6. `Registry.process` dispatches to the app's `WebhookHandler.handle(data:)` with `data.shop == "victim.myshopify.com"` and `data.body` containing the attacker's chosen content, exactly as the documented example shows the app is meant to key work off `data.shop`: [8](#0-7) 
7. The host application processes/stores this attacker-controlled data as though it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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

**File:** docs/usage/webhooks.md (L12-29)
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
  end
end
```
