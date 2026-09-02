### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` (and `topic`, `webhook_id`, `api_version`) purely from unauthenticated HTTP headers, while `HmacValidator` (via `to_signable_string`) only signs the raw request body. `Registry.process` validates the HMAC and then hands the caller a `WebhookMetadata` struct whose `shop` field comes straight from the unverified header, giving host applications an "authenticated-looking" tenant identifier that was never actually bound to the HMAC.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside that signed string: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates only this body-bound HMAC, then dispatches `request.shop` (the unauthenticated header value) directly into `WebhookMetadata`, which is the only identity the host application receives for the webhook's tenant: [4](#0-3) [5](#0-4) 

The intended identity binding is `HMAC-authenticated origin shop == metadata.shop used by the host app for tenant scoping`. Because the header is not part of the signed payload, this equality is never enforced by the gem: any raw body/HMAC pair that is valid for the app's secret (e.g., one legitimately delivered to the attacker's own installed shop, or replayed from a captured delivery) can be resubmitted with an arbitrary `shop-domain` header. `HmacValidator.validate` will still return `true` because the body bytes it hashes are unchanged, yet `WebhookMetadata#shop` will report whatever tenant the attacker chooses. This is the same bug class as the reported analog: a value that is *acted upon* (here, tenant attribution) is not covered by the same authenticity check applied to the rest of the message (here, the HMAC over the body).

### Impact Explanation
Any consumer of this gem's webhook API that uses `WebhookMetadata#shop` to select the tenant context (e.g., to look up which merchant's session/data to update) can be tricked into processing attacker-controlled content under a different (victim) shop's identity — a cross-tenant integrity/confidentiality violation. Since the gem presents `shop` as a validated field of an HMAC-checked request, this is a materially misleading trust boundary baked into the library's own API surface, not merely a documentation gap in the host app.

### Likelihood Explanation
An attacker only needs to be an unprivileged party capable of installing/using the app on any shop (e.g., a free development store) to obtain at least one legitimate `(raw_body, hmac)` pair for their own tenant, then can freely re-issue that same body/HMAC to the app's webhook endpoint with a forged `shop-domain` header value. No access to `api_secret_key` or any privileged credential is required — only the ability to receive/replay a webhook delivery already addressed to a shop the attacker controls.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value verified by the HMAC, or otherwise cryptographically tie the header-derived shop domain to the signed body (for example, by including the relevant headers in `to_signable_string`, or by requiring/validating a separate signed assertion of the shop domain) before exposing it via `WebhookMetadata`. At minimum, the gem's documentation and `WebhookMetadata` should make explicit that `shop` is unauthenticated header data and must not be used alone for tenant-scoping decisions.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers/captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker POSTs the identical body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present).
4. `HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` and finds it equal to `H` → validation succeeds: [6](#0-5) 
5. `Registry.process` invokes the host's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, even though the body actually originated from `attacker-shop.myshopify.com`, resulting in the host app associating attacker-controlled data with the victim's tenant.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
