### Title
Webhook `shop` identity is not covered by the HMAC signature and is passed to handlers unauthenticated - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` validates only covers the raw request body, not this header. An attacker who controls the raw request bytes for a legitimately-signed webhook delivery (or who can otherwise produce a request whose body matches a valid HMAC for a different, attacker-chosen `shop-domain` header) can cause the host app to process the webhook under an arbitrary shop identity, breaking the binding `shop authenticated == shop covered by HMAC`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`. For webhook requests, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

However, `Request#shop` reads the shop identity from the `shop-domain` header, which is not part of the signed bytes at all: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` (from the unauthenticated header) and forwards it to the app's webhook handler as the tenant identity, without any secondary check that the header matches the body or any other authenticated source: [3](#0-2) 

The gem's own validation logic only proves "these bytes were signed by someone holding `api_secret_key`" — it proves nothing about which shop header accompanied those bytes. Any host application that follows the gem's documented pattern (validate via `HmacValidator`, then trust `request.shop` for tenant dispatch, as the gem's own docs/tests demonstrate) inherits this gap, because the gem itself does not bind the `shop` field into the signable content the way it binds `shop` in `Auth::Oauth::AuthQuery#to_signable_string` (compare with the OAuth callback path, where `shop` *is* part of the signed payload): [4](#0-3) 

### Impact Explanation
If HMAC-signed webhook bodies for a given topic can be replayed or partially reused with a substituted `shop-domain` header (e.g., a proxy, load balancer, or any component that forwards genuine signed bodies with attacker-influenced headers, or if two shops produce bodies with colliding/reusable signed content), the receiving application will process/dispatch the webhook under the wrong shop's tenant context. Since `WebhookMetadata.shop` is the identity used by host apps to select per-tenant data/credentials, this is a cross-tenant data-processing issue — the app would act on webhook data believing it belongs to shop A while the identity-binding value it trusts (`shop`) was never authenticated by the same signature that proves the payload's integrity.

### Likelihood Explanation
Exploitability depends on an attacker's ability to influence the `shop-domain` header independently of the signed body reaching the app (e.g., via a misconfigured reverse proxy that forwards Shopify's raw signed body but allows header injection/override, or any component in the delivery chain that separates header handling from body handling). This is not directly exploitable by an anonymous internet user against Shopify's own webhook delivery infrastructure alone, but the root cause — the shop identity field is excluded from the HMAC signable string within this gem — is a genuine design flaw in the library's trust model, independent of how any particular host app is configured.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in the HMAC signable string computed by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop identity to the validated payload, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signed content. At minimum, document clearly that `request.shop` is not covered by HMAC validation and must not be trusted as an authenticated tenant identifier without additional verification.

### Proof of Concept
1. Construct a `ShopifyAPI::Webhooks::Request` with a valid `raw_body` and a correctly computed HMAC for that body using `api_secret_key`.
2. Set the `shopify-shop-domain` header to an arbitrary value (e.g. `"victim-shop.myshopify.com"`) instead of the shop that actually produced the body.
3. Call `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC — it never inspects the `shop` header: [5](#0-4) 
5. `handler.handle` is invoked with `shop: request.shop` set to the attacker-supplied value, demonstrating the identity field flows to the application layer without being covered by the integrity check. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
```
