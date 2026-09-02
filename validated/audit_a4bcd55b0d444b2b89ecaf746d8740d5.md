### Title
Webhook `shop` (tenant) identifier is read from an unauthenticated HTTP header and is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC signature that `ShopifyAPI::Utils::HmacValidator.validate` checks in `Registry.process` [2](#0-1)  only binds the request body. The `shop` value used to identify the tenant, however, is taken directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed bytes [3](#0-2) .

### Finding Description
`Registry.process` validates the webhook by calling `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it to `request.hmac` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) , and `hmac` is read from the `shopify-hmac-sha256` header [5](#0-4) . Meanwhile `shop` is read from the `shopify-shop-domain` header, entirely independent of the signed payload [3](#0-2) .

This breaks the intended identity binding: `HMAC-verified bytes == bytes used to identify the tenant`. In reality, `signed(raw_body) != shop-domain header`, i.e., the shop identity attached to the webhook event is never authenticated by the signature at all - only the body content is.

The `shop` value flows straight into `WebhookMetadata` and is handed to the app's registered handler as the authoritative tenant identifier for the event: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) . The gem's own documentation instructs consuming apps to trust `data.shop` as "The shop domain of the webhook" and use it directly for business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [7](#0-6) .

### Impact Explanation
Because `shop` is not covered by the HMAC, a party who can produce a validly-signed body for *any* known/legitimate webhook payload (e.g., replaying a captured signed request, which is possible because there is no nonce/timestamp binding either) or otherwise submit a request whose header `shop` differs from the value implied by the signed body, can cause the gem to report an attacker-controlled `shop` value to the app while the signature still validates. Since the documented app-level pattern is to trust `data.shop` as the tenant key (e.g., to select per-tenant data, credentials, or job queues), this allows cross-tenant data association/confusion in the app layer: a webhook validated as "authentic" can be attributed to the wrong shop. This matches the High-impact category of "cross-tenant access" resulting from a scope/identity check that doesn't actually bind the checked field.

### Likelihood Explanation
Exploitation requires the attacker to control or manipulate the `shopify-shop-domain` header of a request that Shopify (or a replay of a Shopify request) sends to the app's webhook endpoint, independent of the HMAC-signed body. This is plausible in deployments where the webhook endpoint is reachable and headers can be influenced/replayed (e.g., proxy misconfiguration, request tampering before signature check, or replay of a previously valid signed body with a swapped shop header), since the gem provides no protection binding shop identity to the signature.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, timestamp) fields in the signed/verified data, or otherwise cryptographically bind the `shop` value to the signature before trusting it. At minimum, document/enforce that `WebhookMetadata.shop` must be cross-checked against an independently trusted source (e.g., session store keyed by webhook_id or topic+body-derived shop) rather than being treated as authenticated by the HMAC check.

### Proof of Concept
1. Capture a legitimately Shopify-signed webhook request (raw body `B` with valid `hmac-sha256` header `H`, and header `shopify-shop-domain: victim.myshopify.com`).
2. Replay the exact same body `B` and `hmac-sha256` header `H` (still valid, since HMAC is only over `B`), but replace the `shopify-shop-domain` header with `attacker.myshopify.com`.
3. `HmacValidator.validate(request)` still returns `true` because `to_signable_string` only hashes `@raw_body` [1](#0-0) .
4. `Registry.process` proceeds and calls the app handler with `shop: "attacker.myshopify.com"` even though the signed body content came from `victim.myshopify.com` [8](#0-7) , demonstrating the shop-identity field is unauthenticated relative to the HMAC.

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

**File:** docs/usage/webhooks.md (L10-29)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
