### Title
Webhook `shop` domain is trusted as tenant identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking the HMAC of the raw request body only, then passes the unauthenticated `x-shopify-shop-domain` header value to the app's handler as the trusted tenant identifier. The `shop` field is acted upon by every consumer of the gem (it is documented as "the shop domain of the webhook") but is never part of the signed data, breaking the equality `hmac-verified-bytes == identity used for dispatch`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . None of the Shopify headers — `topic`, `shop-domain`, `api-version`, `webhook-id` — are included in the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and, on success, unconditionally forwards `request.shop` — read directly from the unauthenticated header — to the handler as the shop identity for that webhook payload: [4](#0-3) 

The library's own documentation instructs integrators to treat `data.shop` as the authoritative tenant for dispatching business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) .

Because the HMAC only proves that `body` was produced with knowledge of `api_secret_key` (i.e., it was legitimately emitted by Shopify for *some* shop using this app), it does not bind that body to any particular shop domain. An attacker who is an unprivileged merchant that installs the app on their own store receives their own genuinely-signed webhook deliveries (valid `hmac-sha256` for their own `body`). Since the webhook endpoint is a public URL controlled by the host application and not restricted to Shopify's IP range by this gem, the attacker can directly POST that exact `body`+`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header to name a different (victim) shop. `Utils::HmacValidator.validate` still succeeds, because it never inspects the header, and `Registry.process` dispatches the payload labeling it as belonging to the victim shop.

### Impact Explanation
This breaks the identity binding `shop authenticated == shop stored/acted upon`, one of the explicitly in-scope analog classes ("a field acted on but not covered by the HMAC"). Any application that uses `data.shop` from `WebhookMetadata` to select which merchant's data/session to update (the pattern the gem's own docs recommend) can be made to apply attacker-supplied webhook content under a victim shop's identity — a cross-tenant data-integrity/dispatch violation. This satisfies the Critical impact category "cross-tenant access."

### Likelihood Explanation
Exploitation requires only:
1. The attacker installs the app on a shop they control (a normal, low-privilege action any merchant can take for public apps), and
2. The ability to send an arbitrary HTTP POST to the app's public webhook endpoint with attacker-chosen headers — nothing an unprivileged internet user is prevented from doing, since the gem performs no source/IP validation and headers are excluded from the signature.

No access token, `api_secret_key`, or credential theft is required, satisfying the "unprivileged internet user" constraint.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the value that is cryptographically verified, or otherwise cryptographically bind the header-derived shop domain to the signed body (e.g., require the shop to be independently confirmed against a known/registered value, or fold the header values into the signable string used for HMAC computation) before trusting `request.shop`/`WebhookMetadata#shop` as an authenticated tenant identifier. At minimum, update the documentation to explicitly warn integrators that `data.shop` is not cryptographically bound to the verified payload and must not be used as a sole tenant-authorization key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) for a resource they control, capturing the genuine request Shopify sends: `raw_body`, and header `x-shopify-hmac-sha256` (valid for that body under the shared `api_secret_key`).
2. Attacker POSTs the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` returns `true` because it only checks `raw_body` against the HMAC [2](#0-1) .
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...))` [6](#0-5) , causing the host application to process attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-33)
```ruby
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
