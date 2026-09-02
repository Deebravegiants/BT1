### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so the HMAC signature validated by `Utils::HmacValidator.validate` binds *only* the body bytes to the app's shared secret. The tenant-identifying fields the gem extracts and hands to application handlers — `shop`, `topic`, `webhook_id`, `api_version` — come straight from HTTP headers and are never part of the signed payload.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which (per `VerifiableQuery`/`HmacValidator`) recomputes the HMAC over `to_signable_string` (i.e. body only) and compares it to the `hmac` header: [3](#0-2) [4](#0-3) 

Because the app's `api_secret_key` is a single shared secret across every shop that installs the app (it is not per-shop/per-tenant), any party who can obtain one valid `(raw_body, hmac)` pair for the app — e.g. by installing the app on their own store and capturing a real webhook delivery — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `topic`/`webhook-id`) header to name a *different* shop. `HmacValidator.validate` will still succeed because it never inspects those headers, and `Registry.process` will invoke the topic handler with a `WebhookMetadata` object whose `shop` field names the victim tenant while the `body` content is the attacker's own data: [3](#0-2) 

This breaks the identity binding `shop authenticated == shop acted upon`: the gem cryptographically authenticates the body but not the shop the body is attributed to, yet downstream application code (session/tenant lookup, database writes, business logic) is expected to trust `WebhookMetadata#shop` as the verified tenant identifier.

### Impact Explanation
This allows cross-tenant confusion in webhook delivery: an attacker who is a legitimate (even trial/dev) merchant of the app can forge webhook deliveries that the receiving app will process as if they originated from an arbitrary other shop's store (as long as that shop is also an app installer, which is required for the app to act on it), while providing attacker-controlled body content. Any host application relying on `WebhookMetadata#shop` (returned by this gem) to select the tenant record/session to update — the pattern this gem's own registry/README encourages — will apply attacker data to a different merchant's data, a cross-tenant impact.

### Likelihood Explanation
Requires the attacker to be (or briefly become) an installed user of the target app to legitimately receive one valid `(body, hmac)` pair, which is realistic for freely-installable/dev-store apps. No possession of `api_secret_key` or access tokens is needed — only replay of previously-observed legitimate webhook bytes with a modified header, which is entirely within an unprivileged internet user's capability (they control the HTTP request to the app's own webhook endpoint).

### Recommendation
Bind the shop (and ideally topic/webhook id) into the verified payload rather than trusting headers as-is: e.g., require the host app to cross-check `request.shop` against the shop encoded within the parsed body / against the shop associated with the session that owns the webhook subscription (Shopify provides shop context in the body payload for most topics), or document explicitly that `shop`/`topic` headers are unauthenticated and must be independently verified by callers before using them as a tenant selector.

### Proof of Concept
1. Install the target app on attacker's own shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
2. Resend an HTTP POST to the app's webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (a real shop that also installed the app).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes the HMAC over `@raw_body` (`to_signable_string`) — the forged `shop-domain` header is never checked.
4. The registered handler executes with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's original data>)`, so any tenant-scoped action the host app performs keyed on `data.shop` is executed against `victim.myshopify.com` using attacker-supplied body content.

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
