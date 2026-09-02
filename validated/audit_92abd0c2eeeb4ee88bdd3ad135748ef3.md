### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) claims are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` attribute that handler code uses to identify which merchant/tenant a webhook belongs to, but the HMAC signature verified by `HmacValidator` is computed **only** over the raw request body. The `x-shopify-shop-domain` header (and `topic`, `webhook-id`, `api-version`) is never included in the signed payload, so it can be freely altered without invalidating the HMAC check.

### Finding Description
`Webhooks::Registry.process` authenticates an incoming webhook solely via: [1](#0-0) 

The HMAC validity check delegates to `Utils::HmacValidator.validate`, which computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body — none of the Shopify-supplied headers are part of the signed material: [3](#0-2) 

Yet `shop`, `topic`, `api_version`, and `webhook_id` — all parsed straight from unauthenticated headers — are passed on to the application's handler as trusted identity/routing data: [4](#0-3) 

This reproduces the report's bug class exactly: a field that business logic acts on (`shop`, used to select which tenant's data/session the webhook applies to) is not covered by the cryptographic binding (`hmac`) that is supposed to authenticate the whole message. The equality that should hold is:

`shop_header == shop_that_produced(raw_body, hmac)`

but the gem only proves `hmac == HMAC(raw_body)`, never binding `shop` (or `topic`/`webhook_id`) into that proof.

### Impact Explanation
Any legitimate merchant/tenant of a multi-tenant app receives real, correctly-signed webhooks for their own shop (body + `x-shopify-hmac-sha256`). Because the header set (`shop-domain`, `topic`, `webhook-id`, `api-version`) is not part of the signed string, that same merchant (an unprivileged actor with respect to *other* tenants) can capture one of their own valid webhook deliveries and replay the identical `raw_body`/`hmac` pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` value. `HmacValidator.validate` will still return `true` because it only re-derives the HMAC from `raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to a different shop: [5](#0-4) 

Any app whose webhook handler trusts `data.shop` to route persistence, cache invalidation, or session lookups (as the gem's own docs instruct apps to do) can be made to apply one tenant's data/event under another tenant's identity — i.e. cross-tenant access/data confusion, which is a Critical-tier impact per the given classification.

### Likelihood Explanation
Exploitation requires only capturing one's own genuine webhook (something every installed merchant naturally receives) and replaying it with a modified header via a normal HTTP client — no access to `api_secret_key`, access tokens, or privileged accounts is needed. The only precondition is that the target app's webhook handler uses `shop`/`topic` from `WebhookMetadata` for authorization or tenant-routing decisions, which is the documented and expected usage pattern of this API.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body (e.g., via a canonicalized signed string analogous to `Oauth::AuthQuery#to_signable_string`), so that altering any of these fields invalidates the signature. At minimum, document prominently that only the raw body is authenticated and that header-derived fields must not be trusted for tenant/authorization decisions.

### Proof of Concept
1. As shop A (installed merchant), receive a genuine webhook delivery: body `{"id":123}`, header `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body)` and passes: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the payload actually originated from shop A, demonstrating the unauthenticated identity binding.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
