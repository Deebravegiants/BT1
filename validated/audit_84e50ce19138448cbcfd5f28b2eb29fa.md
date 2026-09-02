### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used to route and attribute webhook data from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` verifies only covers the raw request body, not this header. An unprivileged sender who has any means of obtaining a validly-signed webhook body/HMAC pair for their own shop can replay it against the same endpoint with the `shop-domain` header swapped to a different merchant's domain, and the signature check still passes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an attacker-controllable header with no cryptographic binding to the signed content: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e. the body) and compares it against the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` treats HMAC success as sufficient authentication, then forwards `request.shop` (the unauthenticated header) directly to the handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the webhook payload == shop whose secret/state actually produced that payload`

But because `shop-domain` is excluded from `to_signable_string`, the check only proves *"a request with this body was signed with the app's shared secret"* — it proves nothing about *which shop* that body belongs to. Since the `api_secret_key` is shared across all shops for a given app, any shop that legitimately receives one authentic signed webhook (e.g., a merchant who installs the app in their own store) possesses a valid `(body, hmac)` pair they can freely replay with an arbitrary `shop-domain` header value, spoofing another tenant.

### Impact Explanation
This breaks the shop identity binding used by `WebhookMetadata` (`data.shop`) that host applications rely on to route webhook data to the correct tenant record/database row. An attacker who is a legitimate merchant of the app can forge webhook events "from" a victim shop by replaying their own signed payload with a different `shop-domain` header, resulting in cross-tenant data injection/misattribution in the host application. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: any account that can install the app (an ordinary, unprivileged merchant) automatically becomes a legitimate signer of at least one webhook body/HMAC pair, and the replay requires only sending a crafted HTTP request with a different header value — no secret material, TLS interception, or privileged access is needed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material checked by `HmacValidator`, or have `Registry.process` independently verify that the shop asserted in the header is one that the host application actually expects/has an active session for, rather than trusting the header solely because the body-only HMAC matched.

### Proof of Concept
1. App merchant A installs the app; Shopify sends a webhook to the app's endpoint with body `B`, header `x-shopify-shop-domain: shopA.myshopify.com`, and a valid `x-shopify-hmac-sha256` computed over `B` with the app's shared secret.
2. Attacker (merchant A) captures this `(B, hmac)` pair.
3. Attacker resends a POST to the same webhook endpoint with the same body `B` and same `hmac` header, but sets `x-shopify-shop-domain: shopB.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only, matches the supplied `hmac`, and returns `true`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata` carrying `shop: "shopB.myshopify.com"`, causing the host app to apply shop A's forged data to shop B's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
