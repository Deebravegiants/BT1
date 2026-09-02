This confirms the vulnerability: the gem's documentation explicitly instructs developers to trust `data.shop` (`ShopifyAPI::Webhooks::WebhookMetadata#shop`, sourced from the `Shopify-Shop-Domain` header) as the tenant identifier once `Registry.process` passes HMAC validation, but the HMAC in `Utils::HmacValidator.validate` is computed only over the raw request body via `Webhooks::Request#to_signable_string`, never over the `shop`, `topic`, or `webhook_id` headers. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Title
Webhook tenant identity (`shop` header) is not covered by the HMAC signature validated in `Utils::HmacValidator` — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` value that is subsequently handed to the app's handler as the tenant identifier (`WebhookMetadata#shop`) comes from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, which is never included in the HMAC-signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is derived from the `hmac-sha256` header: [6](#0-5) [1](#0-0) 

`Registry.process` checks `Utils::HmacValidator.validate(request)` — which internally recomputes `HMAC(secret, to_signable_string)` and compares it to the received `hmac` — and, if it passes, immediately builds `WebhookMetadata` using `request.shop` (the unauthenticated header) and dispatches it to the app's handler: [3](#0-2) 

The equality being enforced is:
`HMAC(client_secret, raw_body) == received_hmac`

but the identity binding the app actually relies on is:
`shop_header == shop_that_produced(raw_body, received_hmac)`

These are not the same statement. Because the `client_secret` is shared across every shop that has installed the app, any legitimately signed webhook body (e.g., one the attacker's own store triggers, since the attacker is a real merchant who installed the app and thus owns a valid HMAC-signed payload for their own store) carries a valid HMAC that is completely independent of the `shop` header value. An attacker controlling the raw HTTP request to the app's webhook endpoint can therefore replay the (valid-HMAC, real) body while substituting the `X-Shopify-Shop-Domain` header for a different, victim shop domain. `Registry.process` will accept it as authentic (since HMAC validation never inspects the header) and will invoke the app's handler with `data.shop` set to the victim's domain, per the gem's own documented contract that `data.shop` is "the shop domain of the webhook."

### Impact Explanation
This breaks the tenant/authentication boundary the gem is trusted to enforce for webhook delivery. Any downstream code that uses `data.shop` (as instructed in the gem's own docs, e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) to look up a `Session`/access token, key a database write, or attribute an event to a shop can be tricked into attaching an attacker-controlled body to another tenant's identity, i.e. cross-tenant access/data confusion, using only the app's normal shared `client_secret` (not requiring the victim's own credentials). This matches the Critical "cross-tenant access" impact category since the tenant scoping of otherwise-authentic webhook traffic is not actually authenticated by this gem.

### Likelihood Explanation
Likelihood is High for any app that reaches the network boundary handling this gem's webhook endpoint: the attacker only needs their own valid app installation (to obtain one real HMAC-signed payload) and control over the HTTP request reaching the app's webhook controller (headers are attacker-supplied at the HTTP layer before/at this gem's parsing, since the raw body and headers are passed in verbatim by the host framework). No leaked victim credentials, TLS interception, or social engineering is required — only standard internet-facing HTTP access to the app's webhook endpoint plus a legitimate installation to source a validly signed body.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, `webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind them to the payload before trusting them, e.g. by having `VerifiableQuery#to_signable_string` incorporate the shop domain and topic alongside the raw body, and rejecting the request if that combined value doesn't match a signature computed with the same fields. At minimum, document and enforce that `data.shop` must never be used as an authorization key without an independent, tenant-scoped verification step (such as confirming the shop has an active session/registration for that specific `webhook_id`).

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the target Shopify app and triggers a webhook (e.g. `orders/create`) for their own store, capturing the full raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` where `H = Base64(HMAC-SHA256(client_secret, B))`.
2. Attacker replays this exact request to the app's public webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)` parses this successfully (all three required headers present).
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and compares against `H` — this matches, since only `B` (unchanged) is signed.
5. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: request.parsed_body, ...))`, causing the app to process attacker-controlled body `B` under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-30)
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
```
