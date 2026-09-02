### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then hands the handler `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` as trusted tenant-identifying metadata. However, the HMAC signature covers only the raw request body — none of these header-derived fields are bound to the signature. This is the same class of bug as the reported issue: a value that is checked/verified (the HMAC over the body) is not the same value that is acted upon (the `shop` used to attribute the webhook to a tenant), breaking the intended identity binding `verified_bytes == acted_upon_identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all sourced directly from HTTP headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body only) and compares it against the received `hmac`: [3](#0-2) 

`Registry.process` uses this single check as the sole authentication gate, then dispatches to the handler using the *unauthenticated* `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`: [4](#0-3) 

The documented handler contract explicitly instructs apps to use `data.shop` as the tenant identifier for the webhook (e.g., to key session/store lookups or enqueue per-shop jobs): [5](#0-4) [6](#0-5) 

**Identity binding broken:** the gem implies `verified(hmac_over_body) == authenticated(shop, topic, webhook_id, api_version)`, but in reality `verified(hmac_over_body) ⊄ {shop, topic, webhook_id, api_version}`. Anyone who can capture (or is legitimately sent, e.g., to their own shop's endpoint) one valid `(raw_body, hmac)` pair can replay it to the app's public webhook endpoint with an arbitrary `shop-domain` header (and arbitrary `topic`/`webhook_id`/`api_version` headers) while keeping the body and HMAC untouched. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will invoke the handler believing the webhook came from the forged shop.

### Impact Explanation
This breaks a tenant-authentication boundary: an unprivileged caller who possesses one valid signed webhook body (trivially obtainable from any shop that installs the app, including their own) can cause the receiving app to process that payload while impersonating a different shop via the `shop-domain` header. Since this gem's own documentation directs consuming apps to key downstream logic on `data.shop`, exploiting this leads directly to cross-tenant data corruption/attribution (e.g., writing another merchant's order/product data under the attacker's own payload, or triggering per-shop side effects like billing/inventory jobs against a victim shop) — this maps to the Critical "cross-tenant access" impact category, since it is the gem's own signature-verification contract that is insufficient to bind the identity fields it hands to the handler.

### Likelihood Explanation
Likelihood is moderate-to-high for any app author who follows the gem's documented pattern literally (using `data.shop`/`data.topic`/`data.webhook_id` as authenticated tenant/dedupe keys without separately confirming that the shop is one they've onboarded via OAuth). The webhook endpoint is a public HTTP endpoint by design (Shopify posts to it over the internet), so no privileged credentials are needed to send a forged request — the only requirement is possession of one legitimately-signed body/HMAC pair, which any existing installed shop (including a low-privilege/free-tier attacker's own store) can supply by triggering a webhook-eligible event.

### Recommendation
Include the `shop`, `topic`, `webhook_id`, and `api_version` values in the signable string used for HMAC computation (or otherwise cryptographically bind them, e.g., by having `HmacValidator`/`Request` verify a canonicalized string containing these fields plus the body), so that `Utils::HmacValidator.validate` fails if any of these header-derived identity fields are tampered with relative to what Shopify actually signed. At minimum, document prominently in `docs/usage/webhooks.md` that `data.shop`, `data.topic`, and `data.webhook_id` are not covered by the HMAC and must be independently cross-checked by the consuming app against a known/installed shop list before being trusted as an identity key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (or otherwise obtains one legitimately-delivered webhook).
2. Shopify sends a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same body `B` and HMAC header to the same endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (headers only need to be present, not consistent with the body); `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only checks `B`.
5. `Registry.process` looks up the handler for the (possibly attacker-chosen) topic and invokes it with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
