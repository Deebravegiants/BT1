### Title
Webhook shop-domain header trusted for tenant identification without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](), [File: lib/shopify_api/webhooks/registry.rb]())

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` validate an inbound webhook exclusively by HMAC-signing the raw body, then blindly trust the `shop-domain` (and `topic`/`webhook-id`/`api-version`) HTTP headers to identify which tenant the webhook belongs to. Because the signature only binds the body, an attacker who can obtain one valid `(body, hmac)` pair signed with the app's shared secret can replay that body with an arbitrary `shop-domain` header and still pass validation, breaking the identity binding `webhook.shop == tenant_that_actually_produced_this_signed_payload`.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body — none of the identifying headers are part of the signed content: [2](#0-1) 

`Registry.process` uses this same HMAC check as its sole authentication step, then constructs `WebhookMetadata` directly from the unauthenticated `shop`, `topic`, `api_version`, and `webhook_id` headers and hands it to the app-supplied handler: [3](#0-2) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read straight from HTTP headers with no cross-check against the signed body or against a list of shops known to the app: [4](#0-3) 

The gem's own documentation instructs app authors to trust `data.shop` as the tenant identity for downstream processing (e.g., enqueuing a job keyed by shop): [5](#0-4) 

Since the app's `api_secret_key` is shared across all shops/tenants that install the app (it is not per-shop), any tenant that legitimately receives real, validly-signed webhooks from Shopify (i.e., any merchant who installs the app) possesses valid `(body, hmac)` pairs. That tenant can then replay the same body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) for a different shop. `HmacValidator.validate` will still pass because the signed content (the body) is untouched, but `Registry.process` will report the spoofed shop as `WebhookMetadata#shop` to the handler. This breaks the equality that the report's bug class targets: the *shop the app acts on* is no longer bound to *the shop that actually owns the signed payload*.

### Impact Explanation
This maps to the "Critical – cross-tenant access" category. An attacker who is a legitimate (or trial) installer of the app for their own shop can forge webhook events attributed to a victim shop's domain. If the host application (as documented and demonstrated in the gem's own usage example) uses `data.shop` to select which tenant's session/database record to update, enqueue jobs against, or otherwise act on, the attacker can inject arbitrary webhook payloads (subject to being able to produce a body that is meaningful for the topic, replayed from their own tenant traffic) that the app will process as if they originated from a different merchant's store — a direct cross-tenant boundary violation using only a body/hmac pair the attacker legitimately possesses.

### Likelihood Explanation
Moderate-to-high. Any developer/merchant that can install the app for a shop they control automatically receives genuine, validly-HMAC'd webhook traffic for topics they subscribe to. No access to `api_secret_key`, tokens, or privileged accounts is required — an attacker only needs to be an ordinary merchant/installer and to control the HTTP request sent to the app's webhook endpoint (headers are fully attacker-controlled since they compose the raw HTTP request themselves, they are not verified by TLS/mTLS in this library). This requires the host app to key tenant/session lookups off `WebhookMetadata#shop`, which is the exact pattern the gem's own documentation recommends.

### Recommendation
- Bind the identifying fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the HMAC-signed content, or otherwise cryptographically bind headers to the body, rather than relying on unauthenticated headers for tenant identity.
- Alternatively/additionally, require and document that `Registry.process` callers must independently verify that `data.shop` corresponds to a shop with an existing, valid session/installation before trusting it for any tenant-scoped action, and make this verification part of `Registry.process` itself rather than leaving it fully to app authors.
- Consider validating `shop` against `Utils::ShopValidator` as a defense-in-depth measure, though this alone does not fix the core binding gap since it doesn't prevent cross-tenant replay between two valid, trusted shop domains.

### Proof of Concept
1. Attacker installs the target app for their own shop `attacker-shop.myshopify.com` and subscribes to webhook topic `orders/create`.
2. Shopify sends a legitimate webhook to the app's webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the shared `api_secret_key`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and replays the exact same HTTP request to the app's webhook endpoint, but changes only the header `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only [6](#0-5)  and it matches `H`, so validation succeeds.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [7](#0-6) , causing the host app to process attacker-supplied webhook data as if it belonged to `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
