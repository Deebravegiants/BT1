### Title
Webhook `shop` field is not cryptographically bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identity used to attribute the webhook to a specific merchant is read from an HTTP header that is completely outside that signature. This breaks the identity binding `shop (authenticated by HMAC) == shop (used by the handler)`, mirroring the report's bug class of a check that covers some fields of a structure but omits the one actually used downstream.

### Finding Description
`Webhooks::Registry.process` validates the webhook using only: [1](#0-0) [1](#0-0) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`Utils::HmacValidator.validate` recomputes the signature from `verifiable_query.to_signable_string` and compares it to the supplied HMAC: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns **only the raw body**: [3](#0-2) 

but `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed material: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app, an attacker who installs the app on their own shop receives genuinely-signed webhooks (`raw_body`, `hmac`) for events they themselves can trigger with attacker-chosen body content (e.g. product/order titles). Nothing in `HmacValidator.validate` or `Request#initialize` binds that valid `(raw_body, hmac)` pair to the `shop-domain` header. The attacker can therefore replay that valid body+hmac pair while substituting an arbitrary `x-shopify-shop-domain` header value (a victim merchant's domain). `Registry.process` will treat the HMAC as valid and hand the host application a `WebhookMetadata` object claiming the data belongs to the victim shop: [5](#0-4) 

### Impact Explanation
This breaks the equality that should hold: `shop covered by valid signature == shop attributed to the processed webhook`. In practice this allows an attacker with no access token, no `api_secret_key`, and no privileged account — only the ability to install the same app on a shop they control — to inject attacker-controlled, falsely-attributed webhook events for any other tenant of the app. Any host application logic keyed off `WebhookMetadata#shop` (e.g., writing into per-merchant data stores, triggering per-merchant side effects) can be poisoned with attacker data under another merchant's identity — a cross-tenant impact.

### Likelihood Explanation
Exploitation requires only: (1) install the same third-party app on an attacker-controlled shop to obtain one valid `(raw_body, hmac)` pair with body content the attacker can partially shape, and (2) send an HTTP request to the app's public webhook endpoint with that body/hmac and a forged `shop-domain` header. No secrets or elevated privileges are needed, making this reachable by any unprivileged internet user who can install the app once.

### Recommendation
Bind the merchant identity into the verified material for webhooks — e.g., include the `shop-domain` (and/or `topic`, `webhook-id`) header values in `to_signable_string` for `Webhooks::Request`, or independently verify that `request.shop` matches a shop the receiving app actually expects/has an active session for, before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a genuine webhook with a controllable body (e.g., a product-created payload with attacker-chosen title/metadata) — Shopify signs it with the app's shared `api_secret_key`, producing valid `(raw_body, hmac)`.
2. Attacker captures this `raw_body` and `x-shopify-hmac-sha256` value.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body`/`hmac-sha256` header but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (which only checks `raw_body` against `hmac`) returns `true`; `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker's body — spoofing data as originating from the victim tenant.

### Citations

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
