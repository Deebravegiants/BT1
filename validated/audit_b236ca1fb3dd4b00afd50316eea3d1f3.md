Found it: `ShopifyAPI::Webhooks::Request#shop` returns the `shop-domain` header verbatim, and this value is **not included in the HMAC-signed bytes** at all.

### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which HMACs `request.to_signable_string` (the raw request body only) and compares it against the `X-Shopify-Hmac-Sha256` header. The `shop` value handed to the app's handler, however, comes from the `X-Shopify-Shop-Domain` header, which is never part of the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  and `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding: [2](#0-1) .

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` field: [3](#0-2) . Since `to_signable_string` is only the raw body, the signature proves the body wasn't tampered with, but it proves nothing about which shop the header claims to be.

`Registry.process` uses this same unauthenticated `shop` value to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) .

This is exactly the report's bug class: a field (`shop`) that is *acted on* (used as the tenant identifier dispatched to the handler) but *not covered by the HMAC* that is supposed to authenticate the request — the equality that should hold, `shop_verified == shop_used`, is broken because `shop_verified` doesn't exist; only the body is verified.

### Impact Explanation
Any unprivileged internet user who has captured (or replayed) one legitimate, correctly-HMAC'd webhook body/signature pair for shop A (bodies for common topics are often generic/predictable, e.g. `app/uninstalled`, `shop/redact`) can resend that exact `raw_body` + valid `hmac` header while substituting `X-Shopify-Shop-Domain: shop-b.myshopify.com`. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` will invoke the registered handler with `shop: "shop-b.myshopify.com"`. If the host application keys any per-tenant action (session/token lookup, data deletion, GDPR redaction, uninstall side effects) off `WebhookMetadata#shop` — which is the documented and expected use of this field — this crosses tenant boundaries: cross-tenant action attribution/exfiltration using another shop's data under a forged tenant identity, without needing the app's `client_secret` or any access token.

### Likelihood Explanation
Requires only network delivery of an HTTP POST to the app's webhook endpoint (a public endpoint by design) with a header value the attacker fully controls, and a body that was HMAC-signed for *some* shop (any webhook received by the attacker's own installed test shop is signed with the app's real secret and works for any body/shop pairing, since shop is not part of the signed payload). No secret knowledge, no credential theft, and no privileged position are required — only observation of one legitimate webhook delivery to any shop that has the app installed.

### Recommendation
Include the shop domain in the HMAC-signed material (or otherwise cryptographically bind it), e.g. incorporate `X-Shopify-Shop-Domain` (and ideally `X-Shopify-Webhook-Id`) into `to_signable_string`, or require the caller to independently confirm the header's shop matches a shop the app has an active session/installation for, before trusting `WebhookMetadata#shop` in `Registry.process`.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with body `{}` and a valid `x-shopify-hmac-sha256` computed over `{}` using the app's secret.
2. Attacker replays: `POST /webhooks` with headers `x-shopify-topic: app/uninstalled`, `x-shopify-hmac-sha256: <same valid signature>`, `x-shopify-shop-domain: shop-b.myshopify.com`, body `{}`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers)` parses this; `HmacValidator.validate(request)` succeeds because it only hashes `"{}"` (see `to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` dispatches the handler with `shop: "shop-b.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the signature was never generated for `shop-b`, letting the attacker forge the tenant identity for any webhook body they can capture once.

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
