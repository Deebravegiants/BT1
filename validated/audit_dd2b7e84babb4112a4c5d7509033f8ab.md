### Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while the `shop` value used to attribute the event to a tenant is read from an unsigned HTTP header. This breaks the identity binding `shop verified by HMAC == shop attributed to the event`, mirroring the reNFT report's "field acted on but not covered by the hash" bug class (Problem 1/3: `hook.extraData`/`orderType` used without being part of the signed digest).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the HMAC-signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC secret: [3](#0-2) 

`Registry.process` validates only this body HMAC, then trusts `request.shop` (the unsigned header) as the tenant identity and forwards it directly to the app's handler: [4](#0-3) 

This is the documented, intended contract: `data.shop` is described as "the shop domain of the webhook" and host apps are told to key work off of it (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) 

Contrast this with the OAuth callback flow, where `shop` **is** included inside the HMAC-signed string via `AuthQuery#to_signable_string`: [6](#0-5) 

That asymmetry shows the webhook path is the outlier: nothing cryptographically ties the `shop-domain` header to the signed body, so the equality `shop bound by HMAC == shop delivered to handler` does not hold for webhooks.

### Impact Explanation
An unprivileged internet user who has legitimately received (or otherwise obtained) any single valid `(raw_body, hmac)` pair for the target app — e.g., by installing the app on a shop they control and capturing a real webhook delivery — can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still succeed because it only checks the body, and `Registry.process` will hand the attacker-chosen shop to the host app's handler as if it were an authentic event for that shop. Depending on how the host application uses `data.shop` (as documented, to key merchant records, look up sessions, or drive background jobs), this enables cross-tenant data injection/confusion — processing forged data under another merchant's identity. This falls under "cross-tenant access" impact.

### Likelihood Explanation
Requires no secret, token, or privileged access — only one legitimately captured body+HMAC pair (obtainable by installing the app on any shop, including the attacker's own) and the ability to POST to the app's public webhook URL with a spoofed header. The gem's own API and documentation guarantee this is how `shop` is derived and consumed, so any host app following the documented usage is affected.

### Recommendation
Bind the shop identity to the cryptographic proof, matching how `AuthQuery` includes `shop` in its `to_signable_string`. Concretely, either:
- Extend `Request#to_signable_string` to include the `shop-domain` header value (and topic/webhook-id, if they matter downstream) as part of the signed content compared against the HMAC, or
- Cross-validate the `shop-domain` header against a shop identifier embedded in the verified payload before dispatching to the handler.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and capture one legitimate webhook delivery: raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` with the app's secret, which the attacker never needs to know).
2. POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` — see: [7](#0-6) 
4. `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body `B`: [8](#0-7) 
5. The host app processes forged data attributed to `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-26)
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
