## Title
Webhook shop-domain header is unauthenticated: HMAC covers only the raw body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `webhook_id`, and `api_version` fields directly from unauthenticated HTTP headers, while `ShopifyAPI::Utils::HmacValidator` only validates the raw request body against those headers. Because the shared `api_secret_key` used to compute the webhook HMAC is the same for every shop that installs the app (it is not shop-specific), any merchant who installs the app can capture one of their own legitimately-signed webhook deliveries and replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. The HMAC still validates (it only signs the body), and the handler receives attacker-controlled `shop` data that is not bound to the actually-signing party.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook exclusively via: [1](#0-0) 

which calls `Utils::HmacValidator.validate(request)`. That validator computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns **only** the raw body, never the shop-domain, topic, or webhook-id headers: [3](#0-2) 

Yet `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from those unauthenticated headers and handed to the app's handler unchanged: [4](#0-3) [5](#0-4) 

This is the same class of bug as the referenced report: the value that is *acted on* (here, the shop identity attributed to the webhook payload) is not part of the cryptographically verified data (here, the HMAC-signed bytes). The equality the code implicitly assumes but never enforces is:

`shop_that_signed_the_body == shop_header_in_the_request`

Because `api_secret_key` is a single per-app secret shared across every shop installation (not a per-shop key), any legitimate merchant who installs the app can:
1. Receive an authentic webhook for their own shop (valid HMAC over that body, computed with the app's shared secret).
2. Replay the exact same body + HMAC to the app's webhook endpoint, but with `x-shopify-shop-domain` (or `shopify-shop-domain`) changed to a victim shop's domain.
3. `HmacValidator.validate` still returns `true` because it only checks the body signature, not the shop header.
4. `Registry.process` then invokes the app's handler with `WebhookMetadata` claiming the body belongs to the victim shop: [6](#0-5) 

Downstream apps are documented to use `data.shop` to scope persisted state (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [7](#0-6) 

so this directly crosses the tenant boundary the gem is expected to enforce.

### Impact Explanation
This breaks the shop-identity binding the gem is relied upon to guarantee for webhook processing, enabling cross-tenant data injection/corruption: an attacker-controlled webhook body (from their own shop) can be attributed to an arbitrary victim shop domain, as long as the attacker can guess or otherwise learn a victim's `myshopify.com` domain (which is generally public/discoverable). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The prerequisite is only that the attacker be able to install the app on their own store (an unprivileged, self-service action for any public app) and capture one webhook delivery, which requires no credentials, no `api_secret_key` disclosure, and no TLS interception — they legitimately receive the signed webhook themselves. Replaying it with a modified header is trivial. Likelihood is Medium-to-High depending on how host applications use `data.shop`, but the underlying primitive (HMAC not binding the shop header) is unconditionally present in the gem.

### Recommendation
Bind the shop identity into the verified data instead of trusting the header in isolation:
- Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or
- Require callers to look up an expected shop (e.g., from an existing session/install record) and reject webhooks whose header shop does not match a known active installation before dispatching to the handler, and
- Document prominently that `data.shop` is not itself authenticated by the HMAC and must be cross-checked against the app's installation records before being trusted for tenant-scoping.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a legitimate webhook POST, e.g. body `{"id":1,...}` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the identical body and HMAC header to the same webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)` builds a request whose `hmac` verifies successfully via `HmacValidator.validate`, since `to_signable_string` is only the body: [8](#0-7) 
4. `Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though `victim.myshopify.com` never sent or signed this data: [1](#0-0)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** docs/usage/webhooks.md (L19-30)
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
```
