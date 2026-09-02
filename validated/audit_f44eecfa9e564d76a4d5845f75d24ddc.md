### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator.validate` authenticates the payload bytes only. The `shop` value used by `Registry.process` to dispatch tenant-scoped work is read straight from the `x-shopify-shop-domain` header and is never included in the signed material, breaking the equality "bytes verified == bytes acted on."

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which only signs `@raw_body`. `Request#shop` is derived independently from a header that is not part of that signable string: [2](#0-1) 
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body) using the app's single, shared `client_secret`: [3](#0-2) 
`Registry.process` accepts the request once the body HMAC checks out, then trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the handler, without any additional binding to the shop that actually produced the payload: [4](#0-3) 

Because the `client_secret` is shared by the app across every installed shop (not per-tenant), an HMAC that is valid for one shop's webhook body is also valid for the exact same body replayed with a different `x-shopify-shop-domain` header — the signature check cannot distinguish which tenant the header claims to be, since the header is outside the signed string. The equality that should hold is `shop-domain-header == shop-that-produced(hmac)`; instead, the header is a free variable an attacker can set without invalidating the HMAC, as long as the body bytes are reused verbatim (e.g., replaying a captured webhook of matching topic/shape, or a self-triggered event from an attacker-owned installed shop with a body that satisfies the handler's parsing).

### Impact Explanation
This breaks the tenant identity binding: a party who can obtain any one valid (body, hmac) pair — trivially, by installing the app on their own shop and triggering an event they control — can replay that exact body to the app's webhook endpoint while claiming a victim shop's domain in the header. If the handler uses `WebhookMetadata#shop` to select which merchant's data/session to act on (the intended and documented use of that field), this allows cross-tenant data manipulation or disclosure driven entirely from unauthenticated attacker-controlled header bytes, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus the ability to generate at least one legitimately signed body (achievable via a normal, unprivileged app installation on an attacker-controlled shop, since HMAC verification uses the single app-wide secret and not any shop-specific key). No access to `api_secret_key`, tokens, or the target shop is needed. Likelihood is bounded only by whether the consuming handler code trusts `WebhookMetadata#shop` for authorization/routing decisions, which is the pattern this gem's `WebhookHandler` interface encourages.

### Recommendation
Include the shop domain (and topic/webhook id, if they drive authorization decisions) inside the HMAC-signed material, or otherwise cryptographically bind the header claims to the body before dispatch — e.g., compute/verify the HMAC over a canonical string that concatenates `shop-domain` + body, rather than the body alone. At minimum, document that consumers must independently verify `WebhookMetadata#shop` against an out-of-band trusted source (e.g., confirm the shop has an active, previously stored session) before using it for any tenant-scoped action.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com` and trigger a webhook event whose JSON body is fully attacker-controlled/predictable (many topics allow this, e.g., product/create with attacker-chosen fields).
2. Capture the resulting valid webhook request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Replay the request to the same app's webhook endpoint, keeping `B` and `H` unchanged, but replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)`, which still equals `H`, so `Registry.process` accepts the request: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: B, ...)` and performs whatever tenant-scoped action it associates with `victim.myshopify.com`, even though the payload never originated from that shop.

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
