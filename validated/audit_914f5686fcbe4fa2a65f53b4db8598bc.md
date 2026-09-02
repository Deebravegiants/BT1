### Title
Webhook `shop` identity is trusted from an unauthenticated header while HMAC only covers the body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw body, then hands the handler a `shop` value that is read from an HTTP header never included in that HMAC computation. This mirrors the reported bug class: one field (`collection.key`) is checked while a sibling field required for a correct identity binding (`collection.verified`) is ignored — here, the request body's HMAC is checked while the header-derived `shop` used to identify the tenant is left unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
`to_signable_string` returns only `@raw_body`: [2](#0-1) 
`shop` is pulled from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of the signable string at all: [3](#0-2) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, to_signable_string)` and compares it against the `hmac` header — i.e., it verifies body integrity only: [4](#0-3) [5](#0-4) 

After this check passes, the (unauthenticated) `request.shop` is propagated directly into `WebhookMetadata`, which is the identity the host application's handler acts on: [6](#0-5) [7](#0-6) 

The broken identity-binding equality is:
`hmac_valid_for(raw_body) == true` is treated as proof that `shop_header == tenant_that_generated(raw_body)`, but the gem never establishes that equality — `shop` is read from a header that carries no cryptographic binding to the signed body.

### Impact Explanation
Because the `shop-domain` header is excluded from the signed content, an unprivileged internet user who has legitimately received one authentic `(raw_body, hmac)` pair from Shopify (e.g., by installing the target app on their own store, which is a normal unprivileged action available to anyone) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `shopify-shop-domain` header. `HmacValidator.validate` will still return `true` because it only re-derives the HMAC from `@raw_body`, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. Any host application that trusts `data.shop` to look up or mutate per-tenant state (session revocation, `shop/redact`, `customers/redact`, `customers/data_request`, order/inventory updates, etc.) can be made to act against a different, arbitrary tenant than the one that actually produced the payload — a cross-tenant identity confusion reachable without any credentials.

### Likelihood Explanation
Exploitation only requires an attacker-controlled Shopify development store to install the same public app once (an ordinary, unprivileged action) to obtain one valid `(raw_body, hmac)` pair, then a single crafted HTTP request to the app's webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or the app's server is needed, and the gem's own `HmacValidator`/`Registry.process` code path performs no cross-check between the signed payload and the header-derived shop.

### Recommendation
Bind the `shop` identity to the signed content: either include the shop domain in the HMAC-signed material (mirroring how OAuth's `AuthQuery` includes `shop` in its signable string), or require the host application to cross-verify `request.shop` against a shop value embedded inside the verified JSON body (e.g. a `shop_id`/`shop_domain` field within `parsed_body`) before trusting it for tenant routing. At minimum, document/enforce that `Utils::HmacValidator.validate` guarantees only body integrity and that `request.shop` must not be used as an authenticated tenant identifier without an additional binding check.

### Proof of Concept
1. Attacker creates/owns a Shopify development store `attacker-shop.myshopify.com` and installs the vulnerable app; the app registers a webhook (e.g. `orders/create`) pointing at its public endpoint.
2. Shopify legitimately delivers a webhook to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures this `(raw_body, hmac)` pair (trivial — it's their own store/webhook, no secret needed).
4. Attacker sends a new HTTP POST to the same webhook endpoint with the identical `raw_body` and `hmac` header, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body`. [8](#0-7) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the request never originated from, nor was authenticated for, that shop — enabling cross-tenant data manipulation in any handler that trusts this field.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
