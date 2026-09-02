I have enough evidence to conclude the analysis. The `Request#shop` (and `topic`/`webhook_id`/`api_version`) fields are read from HTTP headers that are entirely outside the HMAC-signed bytes (`to_signable_string` returns only `@raw_body`), yet `Registry.process` trusts `request.shop` as the tenant identity passed to the handler.### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, allowing cross-tenant spoofing of webhook metadata - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and label the webhook to the host application are read from separate, unauthenticated HTTP headers. This breaks the intended identity binding: `hmac == HMAC(secret, raw_body)` says nothing about `shop == request.shop`. This is the same class of bug as the reported issue — a security-relevant field (there, `lender_`-provided fee/treasury addresses; here, the tenant-identifying `shop`) is trusted from attacker-controllable input instead of being cryptographically bound to the authenticated payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read from HTTP headers that are never part of the signed bytes: [2](#0-1) 

`HmacValidator.validate_signature` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e., against the body only: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The documented contract explicitly instructs host apps to use `data.shop` as the tenant key for downstream processing (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) 

Binding broken (as an equality): the gem treats `hmac_valid(raw_body) == true` as proof that `shop_header == actual_source_shop`, but the header is never included in the signed material, so those two are independent.

### Impact Explanation
Since `shop` (the tenant identity) is read from a header outside the HMAC-covered bytes, any party able to submit a request to the app's public webhook endpoint with a validly-signed `raw_body`/`hmac` pair (e.g., replaying/reusing a legitimately-received webhook body for their own shop, captured from a normal, unprivileged app installation) can freely set the `shop-domain` header to a different, victim shop. The gem will report `HmacValidator.validate` as `true` and hand the handler a `WebhookMetadata` claiming the data belongs to the attacker-chosen shop. Any host application following the documented pattern of keying storage, job dispatch, or state changes off `data.shop` will process attacker-supplied data under a victim tenant's identity — a cross-tenant confusion at the gem's trust boundary.

### Likelihood Explanation
Medium, matching the judged severity of the referenced report: it requires the webhook endpoint to be reachable directly (not merely invoked internally by Shopify's infrastructure) and requires the attacker to already have a validly-signed `raw_body`, which they can obtain trivially as any merchant who installs the app and receives their own real webhooks (no `api_secret_key` needed, no privileged access). This does not require intercepting Shopify's traffic to the app; it requires only that the app's webhook route is a normal public HTTP endpoint, which is the norm for this integration pattern.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the data that is authenticated, or otherwise validate them against an authoritative source (e.g., only trust the shop identity from a value tied to the caller's registered app credentials/session, or bind the header values into the HMAC-signed string alongside the body) before constructing `WebhookMetadata`. At minimum, document to consumers that these header-derived fields are unauthenticated and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the app on their own shop (`attacker-shop.myshopify.com`) and lets Shopify deliver a legitimate webhook (e.g., `orders/create`) to the app's public callback endpoint, capturing the exact `raw_body` and the `x-shopify-hmac-sha256` header value.
2. Attacker crafts a new POST directly to the same public endpoint using the identical `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, different `topic`/`webhook-id` values, none of which affect the signature).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and succeeds because the body/signature pair is genuinely valid [1](#0-0) .
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker's own body, ...)` [6](#0-5)  and, per the documented usage pattern, dispatches work keyed to `victim-shop.myshopify.com` [7](#0-6) , achieving cross-tenant data injection without ever knowing the app's `client_secret`/`api_secret_key`.

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
