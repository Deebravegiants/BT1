### Title
Webhook `shop` identity is read from an unauthenticated header outside the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed only over the raw request body, but the `shop` value it hands to the app's handler is read from a separate, unsigned HTTP header. An attacker who possesses **any** valid `(raw_body, hmac)` pair produced with the app's shared `api_secret_key` (e.g., from their own store's installation of the app) can replay it while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the gem will report that data as belonging to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . The `shop` accessor, however, is read straight from the `shop-domain` header without ever entering the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identifier passed to the app's handler: [4](#0-3) 

The gem's own documentation instructs integrators to key per-tenant work directly off this value (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) , so this is the intended, documented usage pattern of the gem, not host-application misuse.

The identity binding that should hold is:
`shop authenticated by HMAC == shop used as the tenant key`
but the gem instead authenticates only `raw_body` and lets `shop` be attacker-controlled, i.e. the equality actually enforced is:
`HMAC(raw_body, api_secret_key) == received_hmac` while `shop` is taken from an out-of-band, unauthenticated header — exactly the "field acted on but not covered by the HMAC" class of bug from the report, applied to tenant identity instead of a numeric field.

### Impact Explanation
Because `api_secret_key` is a single value shared by the app across **all** installed shops (it is not shop-specific), any merchant who installs the app can generate a legitimate `(raw_body, hmac)` pair for arbitrary webhook topics/bodies of their choosing (including mandatory topics like `customers/redact`, `shop/redact`, `customers/data_request`). By replaying that valid pair against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim's domain, the attacker gets the app to process attacker-chosen webhook data under the victim's tenant identity. Depending on the handler implementation (which per the gem's own docs keys directly off `data.shop`), this enables cross-tenant data corruption/injection, false redaction/deletion triggers for a victim shop, or business-logic actions performed against the wrong tenant — a cross-tenant boundary violation.

### Likelihood Explanation
The webhook HTTP endpoint is a public, unauthenticated endpoint by design (Shopify must be able to POST to it without prior handshake), so an attacker can reach it freely. Obtaining a valid `(raw_body, hmac)` pair only requires installing the app on an attacker-owned development/test store — a normal, low-friction action — after which the header substitution is trivial. No access token, refresh token, or `client_secret` leakage is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material, or otherwise cryptographically bind the shop identity to the payload before trusting it. At minimum, `Registry.process`/`WebhookMetadata` should not treat header-derived `shop` as authenticated equivalent to the HMAC-verified body; documentation should explicitly warn that `data.shop` is unauthenticated and must be cross-checked against a shop known to have installed the app (e.g., validated against stored sessions) before being used as a tenant key.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and lets Shopify send a real webhook, e.g. `orders/create`, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header — both valid under the app's shared `api_secret_key`.
2. Attacker POSTs to the app's webhook route with the exact same `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` [6](#0-5) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: request.shop, ...)` where `request.shop == "victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-supplied webhook data as if it originated from the victim's shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
