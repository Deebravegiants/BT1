## Title
Webhook shop/topic/webhook-id identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values that the app uses to route and attribute the webhook are read straight from unauthenticated HTTP headers. This breaks the identity binding `verified_bytes == identity_used_by_app`, allowing a replayed, still-validly-signed payload to be attributed to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that are never part of the signed material: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which internally calls `to_signable_string` (the body only) and compares it against the `hmac-sha256` header using the app's `api_secret_key`: [3](#0-2) [4](#0-3) 

After the HMAC check succeeds, `process` dispatches to the topic handler using `request.topic` and constructs `WebhookMetadata` using `request.shop`, `request.webhook_id`, and `request.api_version` — none of which were included in the signature: [5](#0-4) 

Because Shopify uses the **same app-level `api_secret_key`** to sign webhooks for every shop that has the app installed, an unprivileged attacker who installs the target app on their own store receives genuinely-signed webhook deliveries (valid `hmac-sha256` over a body they fully control/observe). The attacker can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a victim shop's domain. `HmacValidator.validate` still passes because it only checks the untouched body against the same shared secret, so `Registry.process` will accept the forged request and hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

This is the same bug class as the reported Celestia issue: a value the application relies on for a security decision (there, the Merkle key's subtree position; here, the webhook's shop/topic identity) is compared/consumed outside the scope of what was actually cryptographically verified (there, the wrong height offset; here, headers excluded from the HMAC digest).

### Impact Explanation
This is a cross-tenant integrity break: an attacker with no privileges beyond installing the app on their own shop can make the host application process attacker-chosen (their own) webhook data as if it came from an arbitrary victim shop. Depending on how the host app's handlers use `WebhookMetadata#shop` (e.g. updating per-shop state, triggering `app/uninstalled` cleanup, GDPR `customers/redact`/`shop/redact` actions, billing state, or session/access-token bookkeeping keyed by shop), this can lead to cross-tenant data corruption or unauthorized actions performed against a merchant account the attacker does not control — a Critical-severity cross-tenant access primitive per the given impact categories.

### Likelihood Explanation
Requires only that the attacker install the vulnerable app on their own Shopify store (a normal, unprivileged action any developer/attacker can take), capture one legitimate webhook delivery to their own endpoint, and replay it with a modified shop header to the target app's webhook receiver. No access to `api_secret_key`, tokens, or the victim's credentials is needed.

### Recommendation
Bind the identity fields to the signature: include `shop`, `topic`, and `webhook_id` (or otherwise validate them against a value obtained through an authenticated channel, e.g. a mapping already known for that shop from OAuth) in `to_signable_string`, or otherwise reject webhooks whose header-derived shop does not match a shop the app already has an active session/token for. At minimum, document that host applications must independently verify `request.shop` is one of their installed shops before trusting webhook payload data.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a genuinely-signed webhook to the app's endpoint:
   ```
   X-Shopify-Topic: customers/redact
   X-Shopify-Hmac-Sha256: <valid HMAC over raw body B, computed with the app's api_secret_key>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: B
   ```
3. Attacker replays the identical body `B` and HMAC header to the same endpoint, but changes only:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
4. `HmacValidator.validate` recomputes HMAC over `B` only (`to_signable_string` returns `@raw_body`), matching the unchanged `hmac-sha256` header, so validation succeeds. [1](#0-0) 
5. `Registry.process` proceeds to invoke the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the app to treat attacker-controlled data as belonging to `victim.myshopify.com`. [5](#0-4)

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
