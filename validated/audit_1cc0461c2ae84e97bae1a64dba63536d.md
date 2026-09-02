## Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` by reading them straight out of attacker-controlled HTTP headers, but the HMAC signature that `Registry.process` validates only covers the raw request body. This breaks the identity binding that a webhook consumer implicitly relies on: `hmac_valid(raw_body) == metadata_authentic(shop, topic, ...)`. In reality the HMAC only proves `raw_body` was produced with the app's `api_secret_key`; it says nothing about which shop or topic that body belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the body or to the hmac header: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (i.e., only the raw body) and compares against `request.hmac` (derived from the `hmac-sha256` header): [3](#0-2) [4](#0-3) 

Since the signature check succeeds as long as `raw_body` matches, an attacker who can obtain any single valid `(raw_body, hmac-sha256)` pair for the shared `api_secret_key` (e.g., by triggering a real webhook delivery to their own shop, which is entirely legitimate and requires no privileged access) can replay that exact body+hmac to the host app's public webhook endpoint while substituting the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers with arbitrary values. `Registry.process` will pass the forged `shop` straight to the handler as authenticated data: [5](#0-4) 

This is the "field acted on but not covered by the HMAC" bug class from the analog report: `sellerNetProceeds` was computed from a value (`depositedValue`) that silently diverged from the value actually used for fee accounting (`weiPrice`), just as here `data.shop`/`data.topic` diverge from what the HMAC actually authenticates (`raw_body` only).

### Impact Explanation
Any host application that trusts `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) as an authenticated tenant identifier — which is the documented and expected usage pattern shown in `docs/usage/webhooks.md` and exercised in `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` — can be made to process a payload under a different shop's identity. This is a cross-tenant confusion: an unprivileged actor with access to only their own shop's webhook traffic can cause the app to act as though the (validly signed) payload belongs to a shop they do not control, satisfying the "cross-tenant access" Critical impact bucket.

### Likelihood Explanation
The webhook endpoint is a public, unauthenticated HTTP endpoint by design (Shopify calls it over the internet). No secret, session, or privileged credential is needed beyond obtaining one legitimate raw_body+hmac pair, which any merchant/developer using the app already possesses for their own shop's webhooks. Forging headers on an HTTP POST is trivial. Likelihood is high for apps that key any business logic (data isolation, authorization, side effects) off `WebhookMetadata#shop` or `#topic` without independently cross-checking them.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string, or otherwise verify them cryptographically before trusting them — e.g., compute the HMAC over a canonical string combining these header values with the raw body, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`/`host` into its signature. At minimum, document clearly that only `raw_body` integrity is guaranteed and that `shop`/`topic` must be revalidated against the app's own registration/session store before being trusted.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` triggers any real webhook (e.g., `orders/create`); Shopify sends a valid request with `raw_body = B`, `x-shopify-hmac-sha256 = HMAC(B, api_secret_key)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `B` and its valid `hmac-sha256` header value.
3. Attacker POSTs the same `raw_body = B` and same `hmac-sha256` header to the victim app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the hmac header — see [1](#0-0)  and [6](#0-5) .
5. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"`, `topic` and `webhook_id` all attacker-controlled and treated as authenticated — see [5](#0-4) .

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
