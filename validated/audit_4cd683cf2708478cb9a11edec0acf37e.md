Confirmed: the `docs/usage/webhooks.md` example (lines 19-30) explicitly instructs developers to use `data.shop` (taken straight from the unauthenticated `shop-domain` header) as a trust anchor — e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` — while the HMAC only covers the raw JSON body.

### Title
Webhook tenant identity (`shop-domain`) is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates the JSON body alone. The `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly from HTTP headers via `shopify_header`, completely outside the signed material, yet `Registry.process` forwards `request.shop` unmodified into `WebhookMetadata` and hands it to the app's handler as the trusted tenant identifier.

### Finding Description
`Request#hmac`/`to_signable_string` and `HmacValidator.validate_signature` establish the binding: `computed_signature = HMAC(secret, raw_body)` and it is compared only against the `hmac` header. [1](#0-0) [2](#0-1) [3](#0-2) 

`shop` is pulled from the `shop-domain` header, which is never included in the signable string: [4](#0-3) 

`Registry.process` validates the HMAC over the body only, then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the handler: [5](#0-4) 

The equality that should hold — `shop_that_produced(raw_body, hmac) == shop-domain header value` — is not enforced anywhere in the gem. Because the same `api_secret_key` (the app's single `client_secret`) is used to validate every shop's webhooks, and the shop identity is carried purely by an unauthenticated header, any party who can obtain one legitimate `(raw_body, hmac)` pair from Shopify for their own store (a completely unprivileged action — installing the app on their own shop and triggering an event) can replay that exact body+signature to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` faithfully reports the attacker-chosen `shop` to the handler. [6](#0-5) 

The gem's own documentation reinforces the unsafe usage pattern by telling integrators to treat `data.shop` as an authenticated tenant key for routing/persistence: [7](#0-6) 

### Impact Explanation
This crosses the tenant boundary explicitly called out in scope: "the shop authenticated versus the shop stored as a session key." A malicious but otherwise unprivileged merchant (any internet user who installs the multi-tenant app on their own store) can inject attacker-controlled webhook payloads that the host application will process and persist as belonging to a victim shop, since the library gives applications no way to detect that the `shop` value was never cryptographically bound to the body/signature that was validated. This is cross-tenant data injection facilitated entirely by this gem's API surface (`Request`/`Registry.process`/`WebhookMetadata`), matching the High-severity "cross-tenant access" category.

### Likelihood Explanation
High. No secret, token, or privileged access is required — only the ability to install the target app on any Shopify store (a normal, unprivileged action available to any Shopify merchant) and capture one legitimate webhook delivery to that store. The header can then be freely modified on replay because it plays no role in `to_signable_string`, and this is the documented/only verification path (`HmacValidator.validate`) in the gem.

### Recommendation
Bind the tenant identity to the signed material, or at minimum require the host application to independently verify that `request.shop` corresponds to a shop with an active session/installation before trusting it, and document this requirement prominently. Where possible, extend `to_signable_string` (or add a secondary check in `Registry.process`) to assert that the `shop-domain` header value is consistent with an install this app expects, rather than passing it through unauthenticated into `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`).
2. Capture the raw POST body and the `X-Shopify-Hmac-Sha256` header value Shopify sent to the app's registered callback URL.
3. Replay an HTTP POST to the same callback URL with the identical body and `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully; `Utils::HmacValidator.validate` returns `true` because `to_signable_string` only ever returns `raw_body`, unaffected by the header change. [2](#0-1) 
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)`, and the host application processes/records this as legitimate data for the victim's tenant. [8](#0-7)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
