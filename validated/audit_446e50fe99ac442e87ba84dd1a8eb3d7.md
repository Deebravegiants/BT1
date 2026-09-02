### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body with HMAC, while the `shop` (and `topic`) identity used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook to a tenant is read straight from an unsigned HTTP header. An attacker who legitimately installs the app on their own store can replay a self-generated, validly-signed `(body, hmac)` pair while swapping the `x-shopify-shop-domain` header to a victim shop that also has the app installed, and the library will accept it as an authentic webhook for the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from the `shop-domain` header, which is not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (the body) against the received HMAC — it has no knowledge of, and does not bind, the `shop` header: [3](#0-2) 

`Registry.process` calls this HMAC check and then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler, without any additional binding between the verified body and the shop identity used for tenant attribution: [4](#0-3) 

Since the webhook signing secret is the app's single `client_secret`, shared across every shop that installs the app, any merchant who installs the app (an "unprivileged internet user" from the perspective of any other tenant of the same app) can generate a completely valid `(body, hmac)` pair for their own store. Because `shop` is excluded from the signed content, that exact pair can be replayed against the same endpoint with the `x-shopify-shop-domain` header changed to any other shop that also has the app installed. The equality that should hold — *shop authenticated (bound into the HMAC) == shop acted upon (used to key tenant data/handler dispatch)* — does not hold: the HMAC binds only the body, not the shop.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): an app that keys any state off `WebhookMetadata#shop` (e.g., processes `orders/create`, `app/uninstalled`, or GDPR/compliance webhooks and stores/mutates per-shop records keyed by the header-derived shop) can be made to apply attacker-controlled webhook payload data to a victim tenant's account, or to fire a legitimate handler (such as data-erasure or uninstall cleanup logic) against a shop that never triggered that event. This matches the Critical criterion of cross-tenant access via this gem's own dispatch logic, not host misuse — `Registry.process` is the documented, built-in entry point.

### Likelihood Explanation
Exploitation requires only that the attacker be an ordinary merchant who can install the target public app on a store they control (no `api_secret_key`, no leaked credentials, no TLS interception) and that the same app also be installed on a victim shop — a very common configuration for public apps. Capturing a valid `(body, hmac)` pair from their own installation and replaying it with a different `shop-domain` header is trivial with any HTTP client.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed content, or otherwise cryptographically bind the shop identity to the signature verified by `Utils::HmacValidator`, so that `Registry.process` cannot be fed a validly-signed body under an attacker-chosen shop identity. At minimum, document and enforce that consumers must independently verify `request.shop` against a known/installed shop *derived from server-side state established at OAuth time*, not solely from the HMAC check.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` and triggers any webhook topic the app subscribes to, capturing the raw request body `B` and its valid `x-shopify-hmac-sha256` value `H` (both signed with the app's shared `client_secret`).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com` (a shop also known to have the app installed).
3. `Utils::HmacValidator.validate` succeeds because it only checks `H` against `B`: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, causing the app to process attacker data as though it originated from the victim tenant.

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
