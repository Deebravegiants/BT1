Found it: in `Webhooks::Registry.process`, the webhook `shop` field used to identify the tenant for `WebhookMetadata` is taken from the `X-Shopify-Shop-Domain` header, but the HMAC signature (`Request#to_signable_string`) only covers the raw request body — it never binds the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers.

### Title
Webhook tenant identity (`shop`, `topic`, `webhook-id`) not covered by HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by computing an HMAC over `@raw_body` only [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values that drive downstream tenant-scoped handler logic are read straight from HTTP headers that are never included in the signed bytes [2](#0-1) .

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it against the `hmac-sha256` header value [3](#0-2) . For webhooks, `to_signable_string` returns only the raw JSON body [1](#0-0) . Shopify's actual HMAC computation for webhooks is over the raw body too (this matches Shopify's real webhook signing scheme), so the body-only signing itself is expected behavior, not a bug.

However, `Registry.process` uses `request.shop`, sourced from the `X-Shopify-Shop-Domain` header, to build the `WebhookMetadata` passed to the app's handler, establishing which tenant the webhook body belongs to [4](#0-3) . Because `shop`, `topic`, `webhook_id`, and `api_version` are plain headers not covered by the signature, an attacker with a single valid `(hmac, raw_body)` pair captured from one legitimate webhook delivery (e.g., from network logs, a proxy, or any place where webhook payloads transit in plaintext) can replay that exact body with a *different* `X-Shopify-Shop-Domain` header value and the same valid HMAC still validates, since the signature never bound the header claiming which shop the body came from.

This breaks the intended binding: `hmac == HMAC(secret, body)` should imply `shop-header == shop-that-actually-sent-body`, but the code only checks `hmac == HMAC(secret, body)` and trusts the header for tenant identity separately and unconditionally.

### Impact Explanation
An application that trusts `WebhookMetadata#shop` to select which merchant's data (e.g., `customers/data_request`, `orders/create`, mandatory GDPR topics) a webhook payload applies to could have that body attributed to the wrong tenant. This is a cross-tenant data confusion/injection vector: the receiving app processes attacker-chosen webhook content and mis-associates it with an arbitrary shop of the attacker's choosing, all while the library reports the HMAC as "valid."

### Likelihood Explanation
This requires the attacker to already possess one valid `(raw_body, hmac)` pair (e.g. via an intercepted/replayed delivery, a shared logging pipeline, or a webhook endpoint that echoes payloads) — this is not achievable purely as an unauthenticated internet user without some prior capture of a legitimate delivery, so the likelihood is limited to scenarios with a plausible interception/replay opportunity. It does not require the app's `client_secret` or an access token, only observation of one webhook delivery.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook_id` header values in the signed byte-string used for HMAC verification (or otherwise cryptographically bind them to the body), so that a captured `(body, hmac)` pair cannot be replayed under a different shop/topic. Alternatively, document clearly that consumers must not rely on `WebhookMetadata#shop`/`#topic` as authenticated fields without additional application-level idempotency/timestamp checks.

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop-a.myshopify.com`, `topic=orders/create`, with raw body `B` and valid `hmac-sha256` header `H` (`H = HMAC(secret, B)`).
2. Replay a POST to the app's webhook endpoint with the same body `B` and same header `H`, but set `X-Shopify-Shop-Domain: shop-b.myshopify.com` (or a different `X-Shopify-Topic`).
3. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(secret, B) == H`, ignoring the changed headers [1](#0-0) [5](#0-4) .
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied header values, even though only the body was authenticated [6](#0-5) .

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
