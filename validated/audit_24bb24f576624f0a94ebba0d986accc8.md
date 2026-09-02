### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` domain (and topic/webhook id/api version) are read from separate, unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` straight to the app's `WebhookHandler` as the authoritative tenant identifier, without the signature ever binding that value.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are pulled from HTTP headers that are never included in the signed content: [2](#0-1) 

`HmacValidator.validate` only checks `hmac` against `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using the unauthenticated `request.shop` value, handing it to the app's handler as ground truth for which tenant the event belongs to: [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(secret, shop || topic || body)` such that a valid signature proves *both* the body and the claimed shop originated from Shopify for that tenant. Instead, the actual binding enforced is only `hmac == HMAC(secret, body)`, i.e., **shop authenticated ≠ shop bound by the signature**. Any request with a body/HMAC pair that is valid for the shared app secret will pass validation regardless of what `x-shopify-shop-domain` header accompanies it. The `WebhookMetadata.shop` field consumed by the merchant's handler (as documented in `docs/usage/webhooks.md`, used for `shop_domain:` in host apps) is therefore attacker-controllable data flowing through the gem as if it were signature-verified.

### Impact Explanation
Because `shop` is unauthenticated, a party who can obtain one valid `(raw_body, hmac)` pair for the shared app secret — e.g., a merchant using the app who can observe genuine webhook deliveries sent to their own configured endpoint, or via a network position that can view (but not necessarily control) traffic to the app's webhook receiver — can resubmit that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The library will report the HMAC as valid and hand the host application a `WebhookMetadata` claiming an attacker-chosen `shop`, while all other header fields (`topic`, `webhook_id`, `api_version`) are equally unauthenticated. Applications that key persistence, deduplication, or authorization decisions off `data.shop` (as the documentation explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to process or store data under the wrong tenant — a cross-tenant confusion/access issue in how the gem exposes verified vs. unverified webhook data.

### Likelihood Explanation
Exploitation requires the attacker to already possess a genuine valid `(body, hmac)` pair signed with the app's secret — they cannot forge a fresh body/HMAC without knowing `api_secret_key`. This limits the practical attack surface to shop-domain re-labeling of a replayed/observed legitimate webhook rather than fully arbitrary forgery, which somewhat reduces likelihood. However, the design flaw itself — the gem silently trusts an unsigned header as ground truth for tenant identity and documents it as such for downstream use — is directly present in library code and requires no crafted edge cases to reach.

### Recommendation
Bind the `shop` (and ideally `topic`) header value into `to_signable_string`/HMAC verification, or otherwise require the host application to independently confirm the tenant identity (e.g., cross-check `request.shop` against a known/expected shop for the delivery path) rather than passing it through as though it were cryptographically verified. At minimum, update documentation to clearly flag that `WebhookMetadata.shop`, `topic`, `webhook_id`, and `api_version` are NOT covered by HMAC verification and must not be trusted for tenant-identity decisions without additional validation.

### Proof of Concept
1. Attacker's own app-connected shop `attacker-shop.myshopify.com` receives a legitimate webhook delivery: raw body `B` with header `x-shopify-hmac-sha256: H` (valid for the shared `api_secret_key`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `raw_body: B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`, to the app's webhook endpoint.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop: "victim-shop.myshopify.com", hmac: H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B` [5](#0-4) .
4. `Registry.process` invokes the host app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [6](#0-5) , causing the application to process the attacker's own webhook body as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
