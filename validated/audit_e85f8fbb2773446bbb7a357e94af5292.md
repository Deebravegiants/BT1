### Title
Webhook `shop` identity is trusted for tenant dispatch but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` value that the gem hands to the host application's handler for tenant identification is read from an unauthenticated HTTP header. `Registry.process` accepts the request as valid once the body's HMAC checks out, then forwards the header-derived `shop` straight to the app's `WebhookHandler` as trusted tenant context.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which plays no part in the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, and then dispatches to the handler using `request.shop` as the authenticated tenant identifier, alongside the (also validated) body: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header value — it never touches `shop`: [4](#0-3) 

The identity binding that should hold is:
`shop delivered to handler == shop whose secret produced the HMAC`

But the actual binding enforced is only:
`HMAC(raw_body, api_secret_key) == hmac header`

The `shop` header is a field *acted on* (used as the tenant key passed into `WebhookMetadata`) but is not *covered by the HMAC*. Any bytes with a valid `(raw_body, hmac)` pair — for example a genuine webhook delivery for the attacker's own shop, which the attacker fully controls and can capture off the wire since they own that store — can be replayed to the app's webhook endpoint with the `shop-domain` header rewritten to a victim's `myshopify.com` domain. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` passes the forged `shop` on to `handler.handle`, believing it originates from the victim tenant.

### Impact Explanation
This breaks the shop-to-signature identity binding and allows cross-tenant impersonation of webhook origin. A host application's `WebhookHandler#handle` implementation typically uses `data.shop` to look up the corresponding merchant's stored session/access token and to scope any subsequent writes or side effects (e.g. applying the payload's data against "that shop's" records). By spoofing `shop`, an unprivileged internet user who legitimately owns one shop (and thus can generate a valid HMAC-signed webhook for their own store) can trick the app into attributing that traffic to an arbitrary other shop, corrupting per-tenant state or triggering shop-scoped actions for a tenant they do not control. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic but requires an attacker to control at least one installed shop of the target app (to legitimately trigger a webhook and obtain a valid `(raw_body, hmac)` pair), plus the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a forged `shop-domain`/`X-Shopify-Shop-Domain` header — both of which are within reach of an ordinary, unprivileged merchant/internet user and require no access token, `api_secret_key`, or privileged account.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material that `HmacValidator` verifies, or otherwise require the caller to independently confirm the header-derived `shop` corresponds to a shop with an active installation/session before treating it as trusted tenant context in `Registry.process` and `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Attacker triggers the webhook and captures the raw HTTP request Shopify sends to the app, including `X-Shopify-Hmac-Sha256` and the raw body — both valid because they were genuinely signed with the app's `api_secret_key` for `attacker.myshopify.com`.
3. Attacker resends this exact captured request to the app's webhook endpoint, only rewriting `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/hmac pair is untouched: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` reporting `shop = "victim.myshopify.com"`, even though the payload actually originated from the attacker's own store: [6](#0-5)

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
