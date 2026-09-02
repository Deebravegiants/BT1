## Analysis

The reported bug class ("dynamically load WASM provider to avoid crash") is not applicable here — no WASM/TextDecoder usage exists in this gem, and that upstream fix is orthogonal to Ruby code. However, mapping the report's broader signal (a security check that validates one artifact while an unrelated, more consequential field is trusted unchecked) to the in-scope library code surfaces a real identity-binding gap in webhook processing.

### Title
Webhook HMAC does not bind the `shop` (tenant) identity, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC of the body and then trusts `request.shop` verbatim when dispatching to the handler, so the value that identifies *which tenant* the webhook belongs to is never bound to the cryptographic signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers that are not part of the signed payload: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` only ever verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the secret — it has no knowledge of, and does not cover, the `shop` header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's handler, with no cross-check that the shop is the one the signed body actually originated from: [4](#0-3) 

This breaks the identity binding: **shop authenticated by the HMAC (none — HMAC covers only body bytes) ≠ shop consumed by the handler as tenant key (`request.shop`, an arbitrary attacker-controlled header)**.

An unprivileged internet user can exploit this without ever learning the app's `api_secret_key`:
1. Install the target app on their own (free) development/test store. Shopify will legitimately deliver a correctly-HMAC-signed webhook (e.g., `orders/create`) to the app's public webhook endpoint, with `x-shopify-hmac-sha256` computed over the raw body and `x-shopify-shop-domain` set to the attacker's own store.
2. The attacker captures this raw body + valid HMAC (it's delivered to infrastructure they control).
3. The attacker replays the exact same raw body and HMAC to the app's webhook endpoint, but substitutes the `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header with the victim's shop domain.
4. `HmacValidator.validate` still succeeds because the signature check only covers the raw body, which is unchanged. `Registry.process` then invokes the handler with `WebhookMetadata` carrying the victim's shop but attacker-controlled body content.

### Impact Explanation
This enables cross-tenant data injection: a host application that scopes side effects (e.g., updating internal records, triggering fulfillment logic, invalidating caches, writing audit logs) by `WebhookMetadata#shop` will act on the victim tenant using data the attacker fully controls (their own store's order/product/customer payload), since the shop attribution is unauthenticated. This is a cross-tenant boundary violation reachable by any user capable of installing the app on a store they control — no access token, secret, or privileged account required.

### Likelihood Explanation
Likely reachable in most real deployments — the gem's own `Registry.process` API is the documented way host apps handle webhooks, and it directly forwards `request.shop` (unauthenticated) as the trusted tenant key to the handler and treats HMAC success as full request authenticity. Any app publicly reachable and accepting installs from arbitrary stores (typical for public/multi-tenant Shopify apps) is exposed.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically/positionally verify that `shop` corresponds to the signed body — e.g., require callers to independently confirm the delivering shop is one they have an active, previously-established session/install record for before trusting `WebhookMetadata#shop`, and document that `Request#shop` is not covered by the HMAC and must not be used as the sole tenant-scoping key without additional verification (e.g., cross-referencing against the shop of an existing, previously validated session for that webhook's `topic`/`webhook_id`).

### Proof of Concept
```
# 1. Attacker installs app on attacker-shop.myshopify.com, Shopify sends:
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid HMAC of body B computed with app secret>
x-shopify-shop-domain: attacker-shop.myshopify.com
Body: B  (attacker fully controls order contents on their own store)

# 2. Attacker replays identical body B and HMAC, changing only the shop header:
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same valid HMAC, body unchanged>
x-shopify-shop-domain: victim-shop.myshopify.com
Body: B

# HmacValidator.validate(request) => true (only checks body vs HMAC)
# Registry.process dispatches handler with shop: "victim-shop.myshopify.com"
# despite the payload never having originated from Shopify on behalf of victim-shop.
```

### Citations

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
