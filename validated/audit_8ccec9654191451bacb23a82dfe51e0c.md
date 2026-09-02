This confirms the analog. The `shop`, `topic`, `api_version`, and `webhook_id` fields are all read directly from HTTP headers and passed to handler code, but the HMAC signature only covers the raw request body.

### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values that the host application relies on for tenant identification are taken directly from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` [2](#0-1) . Meanwhile `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed body [3](#0-2) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (body HMAC) before dispatching, then forwards `request.shop` unchanged into `WebhookMetadata` given to the app's handler [4](#0-3) . `WebhookMetadata.shop` is a plain, unauthenticated `String` field that handler code is expected to trust as the tenant identity [5](#0-4) .

The binding that should hold is: `hmac == HMAC(secret, body || shop || topic)`, i.e., the tenant-identifying header should be part of the signed material. Instead the gem only enforces `hmac == HMAC(secret, body)`, leaving `shop` completely outside of the verified equality.

### Impact Explanation
Because the app's `api_secret_key`/`client_secret` is shared across every shop that installs the app (it is not per-tenant), any merchant who installs the app can capture a legitimately-signed webhook delivery to their own shop (valid `hmac-sha256` for that body) and replay the identical HTTP body/signature to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still passes because it never inspects the header, and `Registry.process` dispatches the request to the handler with `shop` set to the attacker-chosen victim domain [6](#0-5) . Any host application logic that looks up per-shop state (access tokens, settings, order/customer records) keyed by `WebhookMetadata#shop` will act on data or credentials belonging to the victim tenant, resulting in cross-tenant access/data corruption.

### Likelihood Explanation
Any user of the app who has their own shop installation (a normal, unprivileged tenant) can obtain valid HMACs for arbitrary bodies of their choosing (e.g. by triggering webhook-eligible actions on their own store), and only needs to change one outbound header value to target another tenant. No secret material, TLS interception, or elevated access is required — only the ability to receive and replay one's own legitimately signed webhook.

### Recommendation
Include the shop-identifying header (and/or topic/webhook-id) inside the signed material that `Request#to_signable_string` produces, or otherwise independently verify that the shop asserted by the header matches a shop the app expects for that specific delivery (e.g., cross-check against a known/registered shop-to-secret or shop-to-webhook mapping rather than trusting the header value once the body HMAC passes).

### Proof of Concept
1. App's shared `client_secret` is `S`. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), receiving a POST with body `B` and header `x-shopify-hmac-sha256: HMAC(S, B)` plus `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and finds it valid [1](#0-0) [7](#0-6) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and processes the forged body as if it originated from the victim shop [8](#0-7) .

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
