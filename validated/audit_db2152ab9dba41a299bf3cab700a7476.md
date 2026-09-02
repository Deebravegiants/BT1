### Title
Webhook shop-domain (tenant identity) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verified payload as the raw body only, while the `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` values are read from unauthenticated HTTP headers that are never included in the signed content. `Registry.process` trusts `request.shop` as the tenant identity handed to the app's `WebhookHandler` after validating only that the body HMAC matches.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by comparing a computed HMAC of `to_signable_string` against the `hmac` value [1](#0-0) . For webhook requests, `Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` is read from the `shopify-hmac-sha256` header [2](#0-1) . Critically, `Request#shop` (as well as `topic`, `webhook_id`, `api_version`) is read straight from the `shopify-shop-domain` header and is **not** part of `to_signable_string` [3](#0-2) .

`Registry.process` validates only the body HMAC, then immediately trusts `request.shop` and hands it to the registered handler as the authenticated tenant identity: `Registry.process` calls `Utils::HmacValidator.validate(request)` and then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` for the handler [4](#0-3) . `WebhookMetadata.shop` is a plain `String` field consumed directly by the app's handler implementation as the tenant scope [5](#0-4) .

This breaks the identity binding: `shop authenticated == shop bytes covered by the HMAC` does not hold. The HMAC only proves "this body was signed with our `client_secret`" — it proves nothing about which shop the event pertains to. Since the app's `client_secret` (the HMAC key) is the same across every merchant that installs the app, any merchant who legitimately installs the app can capture a validly-signed webhook delivered for their own store (same raw body, valid signature), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and `x-shopify-webhook-id`, `x-shopify-topic`) headers to name a victim shop. `Registry.process` will accept the signature (body unchanged) and dispatch the handler with the attacker-chosen `shop` value, causing the host application to process/attribute the event as belonging to the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who only needs to be an unprivileged installer of the target app (no access to `api_secret_key`, no admin token, no privileged account) can cause the app to process arbitrary previously-observed webhook payloads under an arbitrary target shop's identity. Depending on how the host app's `WebhookHandler` implementations use `WebhookMetadata#shop` (e.g., to look up/create/update per-shop records, trigger data mutations, or issue actions scoped by shop), this can lead to cross-tenant data corruption or unauthorized actions performed against a victim merchant's records — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic: the attacker only needs one legitimate app install (freely available to any developer/merchant on the Shopify platform) to obtain a validly-signed webhook body/HMAC pair, then can immediately replay it with modified identity headers against the app's public webhook endpoint. No secrets, tokens, or privileged access are required beyond what an ordinary app-installing user already has.

### Recommendation
Bind the tenant/topic identity into the signed content, or otherwise cryptographically tie the `shop-domain` header to the verified HMAC before trusting it. At minimum, `Request#to_signable_string` (or a dedicated verification step in `Registry.process`) should incorporate `shop`, `topic`, and `webhook_id` into the value that is HMAC-verified so that a replayed body cannot be relabeled with attacker-chosen identity headers. Alternatively, maintain and check a lookup of `webhook_id`/topic/shop combinations that have already been verified/registered for that specific shop's subscription, rejecting mismatches.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev/test shop `attacker-shop.myshopify.com`, receiving a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`).
2. Attacker replays the exact same request to the app's webhook endpoint, changing only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) `x-shopify-webhook-id` to an unused id, `x-shopify-topic` unchanged.
3. `HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)`, which still equals `H`, since only `@raw_body` is signed [6](#0-5) ; validation passes.
4. `Registry.process` dispatches the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker's body B>, ...)` [4](#0-3) , causing the app to act on the victim shop's tenant scope using attacker-supplied event data.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
