## Title
Webhook `shop` identity is read from an HTTP header that is not covered by the HMAC signature, enabling cross‑tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) exclusively from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. Because a single `api_secret_key` is shared across every shop that has installed the app, any store owner can obtain a validly-signed webhook body/HMAC pair for their own store and then replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature check still passes because the header is not part of the signed payload, so the application processes attacker-chosen data under a victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop` is read straight from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` only compares the HMAC over `to_signable_string` (the body) against the received signature — it never incorporates `shop`, `topic`, or any other header: [3](#0-2) 

`Registry.process` trusts this unauthenticated `request.shop` value and forwards it straight into the handler as the tenant identifier, with no secondary binding to the signature: [4](#0-3) 

Because `Context.api_secret_key` is a single, app-wide secret (not a per-shop secret), a valid HMAC only proves "Shopify (or holder of the secret) produced this body" — it does not prove *which* shop the body pertains to. The `shop` binding the developer relies on (`hmac verified body == webhook belongs to shop X`) is broken: the equality that should hold is `HMAC-covered bytes == identity used by handler`, but here `identity used by handler (header)` is disjoint from `HMAC-covered bytes (body only)`.

### Impact Explanation
Any actor who can install the target app on a shop they control (a normal, unprivileged action available to any merchant) can capture a legitimately-signed webhook (body + `X-Shopify-Hmac-Sha256`) delivered to their own store, then replay that exact body/signature pair to the app's public webhook endpoint while setting `X-Shopify-Shop-Domain` to a victim shop's domain. `HmacValidator.validate` will accept it, and the application will process the payload as if it originated from the victim tenant — e.g., updating the victim shop's local records, triggering a `shop/redact`/`customers/redact` handler, or executing any app-defined webhook business logic against the wrong tenant's data. This crosses a tenant boundary purely through the gem's own signature-verification contract, matching a Critical cross-tenant access impact.

### Likelihood Explanation
Exploitation requires no special access beyond being able to install the app on one's own store (or otherwise observing one legitimate webhook delivery) and the ability to POST directly to the app's public webhook callback URL — both are attacker-reachable without any credentials, tokens, or privileged access. The only "trick" is that the shared app secret and body-only HMAC scheme were never designed to bind the shop header, so the header can be freely substituted.

### Recommendation
Do not trust `request.shop` (or any other webhook header) as an authoritative tenant identifier unless it is cryptographically bound to the verified payload. At minimum:
- Cross-check `request.shop` against the shop embedded in the webhook body itself (most Shopify webhook payloads include shop-scoped identifiers), or
- Require callers to look up a per-shop secret/session and verify the HMAC using that shop's own credentials rather than a single app-wide secret, or
- Document prominently (and ideally enforce in `HmacValidator`) that `shop` must never be treated as authenticated without an independent binding, e.g. reconciling it against the registered webhook subscription's shop.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed webhook topic (e.g., updates a product) and captures the resulting POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `Utils::HmacValidator.validate` recomputes HMAC over `B` and finds it matches `H` (per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31), so validation succeeds.
5. `Registry.process` (lib/shopify_api/webhooks/registry.rb lines 188-199) invokes the app's handler with `shop: "victim-shop.myshopify.com"` even though the body content and signature were produced for `attacker-shop.myshopify.com`, causing the app to act on/mutate data under the victim tenant's identity.

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
