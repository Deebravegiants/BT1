### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC of the raw request body, then unconditionally trusts the `shop`, `topic`, and `webhook_id` values taken from HTTP headers to route the payload and attribute it to a tenant. Because the signable string is the raw body only, none of these identity-bearing fields are covered by the signature, breaking the binding `hmac == HMAC(secret, body + shop + topic)` that the host app implicitly relies on.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers and are not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which computes the signature over `to_signable_string` (i.e., the body alone) and then immediately trusts `request.topic`, `request.shop`, and `request.webhook_id` to select the handler and build `WebhookMetadata`: [3](#0-2) [4](#0-3) 

Shopify signs all webhooks for an app with the same app-level `client_secret`, regardless of which shop triggered the event, and this gem's HMAC check only certifies "this body was produced by holder of the secret" — it does not certify "this body came from shop X" or "this body is topic Y", because `shop`/`topic`/`webhook_id` never enter `to_signable_string`. This is the direct analog of the C4 finding: a field that is acted upon (`shop`, used as the tenant key for `WebhookMetadata`) is not covered by the integrity check (the HMAC), so the binding `hmac-verified-body == shop-attributed-to`  does not hold.

### Impact Explanation
An unprivileged actor who can obtain one legitimate signed webhook body (e.g., by installing the app on their own store and capturing a webhook they legitimately received) can replay that exact `raw_body` + `hmac-sha256` header pair while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header for a different shop. `HmacValidator.validate` will still succeed because the signature check never inspects those headers, and `Registry.process` will dispatch the payload to the app's handler tagged with the attacker-chosen `shop`/`topic`, causing the host application to process cross-tenant data under the wrong shop's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up sessions, write to shop-scoped records, or trigger shop-scoped side effects), this can lead to cross-tenant data corruption/injection — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(raw_body, hmac)` pair, which is trivially obtainable by any developer/merchant who installs the app (an unprivileged, non-credentialed actor from the app's perspective) and receives their own legitimate webhook. No access token, `api_secret_key`, or privileged account is needed — only the ability to send an HTTP request to the app's webhook endpoint with forged Shopify headers, which is exactly the "unprivileged internet user" threat model.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`/timestamp) in the signed/verified material, or independently verify that the `shop` domain in the header matches a shop that legitimately has this exact `webhook_id` registered (e.g., via a nonce/id lookup) before dispatching to handlers. At minimum, document that `Registry.process` HMAC verification does not authenticate the `shop`/`topic` headers and require host apps to independently corroborate `shop` before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger an event so Shopify sends a legitimate webhook with body `B` and header `shopify-hmac-sha256: H` (computed by Shopify with the app's shared `client_secret`).
2. Capture `B` and `H`.
3. Send a POST to the app's webhook endpoint with the same `B` and `H`, but with headers set as:
   - `shopify-topic: <victim-relevant-topic>`
   - `shopify-shop-domain: victim-shop.myshopify.com`
   - `shopify-webhook-id: <arbitrary>`
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only hashes `B` against the secret: [5](#0-4) 
5. `Registry.process` proceeds to call the registered handler with `WebhookMetadata.new(topic: "<victim-relevant-topic>", shop: "victim-shop.myshopify.com", ...)`, causing the host app to process attacker-supplied data as if it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
