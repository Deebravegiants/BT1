### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by the webhook HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but `to_signable_string` — the value that `Utils::HmacValidator` actually signs/verifies — is only the raw request body. The `shop` field is never part of the signed material, so it can be freely set by anyone who can reach the webhook endpoint and supply a body+HMAC pair that is valid under the app's single, shop-independent `client_secret`.

### Finding Description
`Registry.process` authenticates an inbound webhook solely by checking `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` using `Context.api_secret_key` (the app-wide secret shared across every installed shop, not a per-tenant secret): [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

but `shop` is read straight from an unauthenticated header with no cross-check against the signed body: [4](#0-3) 

`Registry.process` then forwards this unauthenticated `shop` value directly into `WebhookMetadata`, which is the only tenant-identifying field the host application's handler receives: [5](#0-4) [6](#0-5) 

The equality that should hold — `shop-in-signed-material == shop-acted-on-by-handler` — does not: `HMAC(raw_body, client_secret)` binds only the body, while `WebhookMetadata#shop` is populated from `x-shopify-shop-domain`, a value with zero cryptographic linkage to the signature or the body.

### Impact Explanation
Because `client_secret` is one value shared by every shop that has installed the app (not per-tenant), any user who legitimately installs the app on a shop they control receives genuine webhook deliveries with valid `(raw_body, hmac)` pairs signed under that same shared secret. That attacker can replay a captured `raw_body`/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept it (the HMAC only covers the body) and hand the host application a `WebhookMetadata` claiming the payload originated from the victim shop. Depending on how the host app keys its tenant data/store lookups on `WebhookMetadata#shop` (a pattern this gem's own webhook API encourages, since `shop` is the only identity field exposed), this enables cross-tenant data injection — e.g., forging `app/uninstalled`, `customers/data_request`, `shop/redact`, or order/customer webhooks under a victim shop's identity, causing the host app to act on/mutate the wrong tenant's records.

### Likelihood Explanation
Exploitation requires only an internet-reachable webhook endpoint and a normal, unprivileged app installation by the attacker (something any user can do for a public/embedded app) — no access token, no `client_secret` leak, and no privileged account is needed. The attacker never needs to know the secret; they only need one legitimately-signed payload from their own shop to replay with a forged header. This is a straightforward, low-effort attack path reachable by any unprivileged user of the app.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) in the signed material, or otherwise cryptographically bind the asserted shop to the request before trusting it — e.g., verify `request.shop` against a shop value embedded in `raw_body` (Shopify webhook payloads include the shop domain in most topics) or against a store of shops known to have completed OAuth/have an active session, before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-scoping without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged installation).
2. Shopify delivers a legitimate webhook to the app's endpoint, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(B, client_secret)` — `client_secret` being the single secret shared by all shops using this app.
3. Attacker replays the exact same request to the app's webhook endpoint, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged, but replacing:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com` → `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (headers required, no shop check), and `Utils::HmacValidator.validate(request)` returns `true` since it only recomputes HMAC over `B`. [7](#0-6) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...))`, and the host app's handler acts on attacker-controlled data believing it belongs to `victim-shop.myshopify.com`.

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
