This confirms the finding: the docs explicitly state the gem's `process` method "will verify the request did indeed come from Shopify" as a single unit, and app authors (per the documented example) are expected to trust `data.shop` as the authenticated tenant identity, but the `shop` field is not covered by the HMAC.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using only `Utils::HmacValidator.validate`, which HMACs the raw request body. The `shop` (and `topic`, `webhook_id`, `api_version`) header values are never included in the signed material, yet `process` trusts `request.shop` as the authenticated tenant identity and hands it straight to the app's handler via `WebhookMetadata`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  and `hmac`/`shop` are parsed independently from headers that are never fed into the signature: [2](#0-1) . `HmacValidator.validate_signature` recomputes the HMAC purely over `to_signable_string` and secure-compares it to the `hmac` header: [3](#0-2) . `Registry.process` raises only if that body-only HMAC fails, then immediately passes `request.shop` (an unauthenticated header) into `WebhookMetadata` and the app handler: [4](#0-3) . `WebhookMetadata.shop` is a plain, unvalidated `String` field: [5](#0-4) .

This breaks the identity binding: `shop_header == shop_that_generated_and_was_authorized_for_this_body` is never enforced — only `hmac_header == HMAC(secret, body)` is enforced. The gem's own documentation instructs app authors to key their business logic off `data.shop` as if it were an authenticated tenant identifier ("shop, String - The shop domain of the webhook"), reinforcing that host apps are expected to trust this field.

### Impact Explanation
Any actor who can obtain one legitimately-signed webhook body+HMAC pair for the app's `client_secret` (e.g., by installing the app on their own store and receiving a real webhook) can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. The signature check still passes because the header is outside the signed scope, and the handler receives `data.shop` set to a victim domain instead of the true origin shop. If the host app uses `data.shop` to select per-tenant state, credentials, or write paths (as the documented usage pattern encourages), this enables cross-tenant data confusion/injection — attacker-controlled webhook content attributed to a shop the attacker does not control.

### Likelihood Explanation
Requires only an app installation the attacker legitimately controls (a normal, unprivileged action for anyone who can install a public/embedded Shopify app) plus the ability to POST to the app's public webhook endpoint with custom headers — no `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the verified body before constructing `WebhookMetadata`, so that `process` cannot be tricked into attributing one shop's signed payload to another shop.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook POST (raw body `B`, header `shopify-hmac-sha256: H`, `shopify-shop-domain: attacker.myshopify.com`) sent by Shopify — `H` is a valid HMAC of `B` under the app's `client_secret`.
2. Replay the same body `B` and HMAC `H` to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` ( [6](#0-5) ) succeeds because it only checks `B` against `H`.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)` ( [7](#0-6) ), causing the app to act on attacker-supplied content as though it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
