### Title
Webhook `shop` field is trusted for tenant attribution but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, but exposes `shop` (from the `x-shopify-shop-domain`/`shopify-shop-domain` header) as a trusted, HMAC-independent field that `Webhooks::Registry.process` forwards directly into the handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read straight from an HTTP header with no cryptographic binding to that signature [2](#0-1) . `Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the received `hmac` [3](#0-2) , so for a `Webhooks::Request`, the signature check equality is `HMAC(secret, raw_body) == received_hmac`, and this holds independent of whatever value is placed in the `shop-domain` header. `Registry.process` validates only that equality and then forwards the *unauthenticated* `request.shop` value straight into `WebhookMetadata`, which is the tenant-scoping value handlers use to process the payload [4](#0-3) .

The broken identity binding, stated as an equality: the gem treats `HMAC_valid(body) == true` as proof that `request.shop == <the shop that actually sent this payload>`, but the signature only proves `HMAC(secret, body)` matches — it says nothing about which shop's `shop-domain` header accompanied that body.

### Impact Explanation
Because `shop` is excluded from the signed content, a party in possession of one previously-observed valid `(raw_body, hmac)` pair (webhooks are delivered over HTTP and are not confidential in transit/at rest for typical logging/proxying setups, and many webhook bodies are non-secret, predictable, or shared shapes) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` whose `shop` field is attacker-chosen, potentially causing the host application to apply another shop's webhook payload as if it belonged to a different, attacker-selected tenant — a cross-tenant data/identity attribution issue.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(body, hmac)` pair for the target app (e.g., from a shop they control, from logs, or from a shared/predictable payload) — no knowledge of `api_secret_key` is needed to forge the substitution itself, only to have observed one valid signed body already produced with that secret. This is a moderate-likelihood scenario since webhook capture is plausible in many deployment setups (misconfigured logging, shared infra, apps installed on attacker's own store to harvest a valid signature, then replay with a victim shop's domain header).

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or have `Registry.process`/host applications independently verify that the `shop` value corresponds to a shop with an active installation/session before trusting it for any tenant-scoped action, rather than relying solely on body-only HMAC verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com`, triggering a webhook delivery with body `B` and header `x-shopify-shop-domain: attacker.myshopify.com`, signed as `H = HMAC(secret, B)`.
2. Attacker captures `(B, H)` from the delivered request (e.g., via a debug proxy they control, or if `B` is a generic/predictable payload shape shared across shops).
3. Attacker sends a forged HTTP request to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes [5](#0-4) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-supplied data under the victim's tenant context [6](#0-5) .

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
