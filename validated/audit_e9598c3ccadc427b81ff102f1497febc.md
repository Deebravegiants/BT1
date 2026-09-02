### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` (parsed from the `x-shopify-shop-domain`/`shopify-shop-domain` header) is read separately and forwarded to the app's webhook handler as the tenant identifier, without being bound to the HMAC signature that `HmacValidator` checks.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook only by checking `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` for the signed content: [1](#0-0) 

`Request#to_signable_string` returns `@raw_body` only: [2](#0-1) 

Meanwhile `Request#shop` is parsed independently from the `shop-domain` header and is *not* part of the signed bytes: [3](#0-2) 

`HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` (the raw body) using the app's global `api_secret_key` (the same secret is shared across every shop that installs the app) and compares it with `secure_compare`: [4](#0-3) 

Because the secret is shared across all shops/tenants of the app, an unprivileged internet user can install the public app on their own shop, receive a legitimately signed webhook (`raw_body` + valid `hmac`), and then replay that exact `raw_body`/`hmac` pair directly to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop). `HmacValidator.validate` still returns `true` because it only checks the body bytes, not the shop header. `Registry.process` then invokes the handler with `WebhookMetadata` built from this unverified `shop`: [5](#0-4) 

The equality that should hold is: `shop_bound_by_hmac == shop_delivered_to_handler`. In reality, the HMAC only binds `body`, and `shop` passed to the handler is attacker-controlled while the signature still validates. The gem's own documentation confirms host apps are expected to trust `data.shop` as the tenant key to route/attribute the payload (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [6](#0-5) 

### Impact Explanation
This allows a cross-tenant identity confusion: an attacker who is merely an installer of the app on their own (unprivileged, e.g. dev/free) shop can forge webhook deliveries that pass this gem's `HmacValidator.validate` check while claiming to originate from any other shop of their choosing. Any host application that relies on the gem's webhook validation + `data.shop` to select the tenant context (session/access-token lookup, data attribution, background job dispatch) will process attacker-supplied body content under a victim tenant's identity — a cross-tenant access/confusion vulnerability that directly matches the mandated Critical-impact category ("cross-tenant access").

### Likelihood Explanation
The precondition (installing a public app on one's own shop to obtain a validly signed body/HMAC) is trivially available to any unprivileged internet user, and the webhook endpoint is a normal public HTTP route reachable by anyone, not restricted to genuine Shopify-origin requests by this gem. The only work required is capturing one legitimately delivered request and re-POSTing it with a modified `shop-domain` header.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) values into the signed content checked by `HmacValidator`, or otherwise independently authenticate that the `x-shopify-shop-domain` header corresponds to the shop that is entitled to send this specific `raw_body`/`hmac` pair (e.g., verify against a shop-specific credential/allow-list instead of trusting an unauthenticated header field forwarded verbatim to `WebhookMetadata`).

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com`, which is entitled to receive real webhooks signed with the app's shared `api_secret_key`.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
4. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` (unchanged) and succeeds against the app's shared secret (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own webhook payload>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled data attributed to the victim tenant.

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
