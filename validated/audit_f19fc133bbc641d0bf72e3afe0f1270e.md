## Title
Webhook `shop-domain` Header Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate`, but the HMAC signature only covers the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from unauthenticated HTTP headers and handed to the webhook handler as trusted identity data. This breaks the binding `hmac_signer_identity == shop_acted_on`, letting any holder of one legitimately-signed webhook payload replay it while spoofing an arbitrary victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly out of HTTP headers, which are not part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e. the raw body) and compares it against the `hmac-sha256` header: [3](#0-2) 

`Webhooks::Registry.process` treats a passing HMAC check as proof the entire request — including `request.shop` — is authentic, and forwards it unchanged to the app's handler: [4](#0-3) 

Because the app's `client_secret` (used to compute the HMAC) is the same for every shop that installs the app, any merchant that installs the app can receive a genuinely-signed webhook (body + valid `hmac-sha256`) for their own store. They can then replay that exact body/HMAC pair to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers to name a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspects those headers, so `Registry.process` calls the handler with a `WebhookMetadata` claiming the victim's shop domain paired with attacker-controlled body content.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: the shop identity delivered to the app's business logic is not actually bound to the cryptographic proof of authenticity. For mandatory topics such as `shop/redact` or `customers/redact` (handled through this same `process` path) an attacker-controlled shop could trigger data-erasure or other tenant-scoped side effects attributed to a shop they do not control — a cross-tenant access/integrity violation, which is Critical severity per the scoring rubric ("cross-tenant access").

### Likelihood Explanation
Any developer/merchant can install the target app on their own store, capture one legitimate webhook delivery (body + `hmac-sha256`), and replay it with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged access is required — only the ability to install the app once and issue an HTTP POST, which is available to any unprivileged internet user acting as a merchant.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) as part of the material verified by the HMAC check, or, more practically, mirror Shopify's actual verification model: keep computing the HMAC over the raw body only, but explicitly document/enforce that `request.shop` must never be treated as authenticated on its own — instead derive/validate the shop from a source that is bound to the signature (e.g., require the app to independently confirm the shop has this webhook subscription/app installation before trusting the header), or require the HMAC be computed over a canonical string incorporating the header values that the handler relies on for tenant identification.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; wait for Shopify to deliver any webhook (e.g., `orders/create`) to the app's endpoint. Capture the raw POST body and the `X-Shopify-Hmac-Sha256` header value — both are valid because Shopify signed them with the app's shared `client_secret`.
2. Replay the exact same body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and, if desired, `X-Shopify-Topic` to `shop/redact` or another mandatory topic, and `X-Shopify-Webhook-Id` to any value).
3. `Webhooks::Request.new` accepts the forged headers since only `topic`, `hmac-sha256`, and `shop-domain` presence is checked, not their consistency with the body.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `@raw_body`, which is unchanged and still matches the signature.
5. `Registry.process` invokes the app's handler with `WebhookMetadata` claiming `shop: "victim.myshopify.com"`, even though the payload actually originated from the attacker's shop — a cross-tenant spoof.

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
