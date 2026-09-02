## #Title
Webhook `shop-domain` header trusted as tenant identity without HMAC coverage, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values come from HTTP headers that are never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` still passes `request.shop` straight into `WebhookMetadata` and hands it to the app's handler as the authoritative tenant identifier. This is the same class of bug as CVE-2016-8624: the identity-bearing component (`host`/`shop`) is not covered by the same verification that protects the rest of the message, so bytes that are verified (the body) and bytes that are trusted for identity (the header) diverge.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC against `to_signable_string` (the body) and, once it passes, unconditionally trusts `request.shop` to build the tenant-scoped `WebhookMetadata` delivered to the host app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — it has no knowledge of, and does not bind, the `shop` header: [4](#0-3) 

The broken equality is: `HMAC-verified bytes (raw_body) == identity bytes the app acts on (shop header)`. Because the app's `client_secret`/HMAC key is shared across every shop that installs the app, any shop that has installed the app can capture a legitimately-signed webhook delivery for its own store (valid HMAC over its own body) and replay that exact body with a different `shopify-shop-domain` header value pointing at a victim shop. `Registry.process` will still pass HMAC validation (since only the body is checked) and will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: a host application that keys per-shop side effects (data storage, cache invalidation, entitlement changes, redaction/GDPR request handling, etc.) off `WebhookMetadata#shop` can be made to associate an attacker-controlled shop's webhook body with a victim shop's identity. Depending on the handler's logic, this enables cross-tenant data confusion/injection, which matches the Critical "cross-tenant access" impact bucket, since the crossing works purely by replaying a self-obtained, validly-signed webhook with a modified shop header — no access token, secret, or privileged account is needed beyond having installed the app as any tenant.

### Likelihood Explanation
Any unprivileged user who can install the target app on their own (potentially free/trial) store can trigger a webhook for that store, capture the exact raw body + valid `hmac-sha256` header Shopify sends, and replay it to the app's own webhook endpoint with the `shopify-shop-domain` header swapped to a target shop. `ShopifyAPI::Webhooks::Registry.process` performs no additional binding check between the header and the signed body, so the replay passes verification deterministically. No cryptographic material or privileged credentials beyond a self-service app install are required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-verified signable content, or independently verify that `request.shop` corresponds to a shop session/store the app actually expects for that specific installation before constructing `WebhookMetadata`. At minimum, `Utils::HmacValidator` (or `Registry.process`) should bind the header-derived identity fields into the signature check rather than relying solely on body-hash equality.

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed with the app's shared secret over `B`).
2. Replay the exact same request to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)` and processes attacker-supplied data under the victim shop's identity.

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
