### Title
Webhook shop/topic/id headers are trusted without being bound to the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers and passed straight to the webhook handler as the tenant/event identity. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands the handler `shop: request.shop` without ever checking that the `shop` header is bound to the signed payload. This breaks the identity binding `HMAC(payload) == HMAC(shop ‖ topic ‖ body)` down to `HMAC(payload) == HMAC(body)`, letting anyone who can obtain one genuinely-signed webhook body (e.g., by installing the public app on a shop they control) relabel it to any other shop and have it accepted as if it originated from that other tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all sourced from HTTP headers that are not part of that signable string: [2](#0-1) 

`HmacValidator.validate` signs/verifies exactly `verifiable_query.to_signable_string`, i.e. the body alone: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` to the handler as trusted identity/metadata for the event, with no further check that `shop` corresponds to the body that was actually HMAC-signed: [4](#0-3) 

Because the shop identity is acted upon (`data.shop`) but not covered by the HMAC, the equality the gem implicitly relies on — "the shop that receives/produces this signed payload equals the shop the handler is told about" — does not hold. Any attacker who can obtain a validly HMAC-signed body for the shared app secret (trivially possible for a public app, since every shop the merchant controls receives genuinely signed webhooks from Shopify) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header for a different, victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` calls the handler with `shop: <attacker-chosen value>`, `topic: <attacker-chosen value>`, and the attacker's own (but validly-signed) body.

### Impact Explanation
This crosses a tenant boundary: the host application's handler code (built on `WebhookMetadata#shop`/`#topic`) is designed to trust these fields as authenticated identifiers for routing/persisting per-tenant data. An attacker with a legitimate install of the same public app (no special privilege beyond being a normal merchant) can forge which shop and topic a genuinely-signed payload is attributed to, causing cross-tenant data injection/spoofing in the host application — matching the "Critical - cross-tenant access" impact bucket, since the vulnerable binding lives entirely inside this gem's `Request`/`Registry`/`HmacValidator` code paths, not in host-app misuse.

### Likelihood Explanation
Any account able to install the target public app on a shop it controls receives real, validly HMAC-signed webhook deliveries from Shopify for that shop. Replaying that body with a substituted `shop`/`topic` header against the same app's webhook endpoint requires no credentials beyond normal HTTP access and no knowledge of `api_secret_key`. This is a low-effort, no-special-access attack path once the app is publicly installable.

### Recommendation
Include the relevant identity headers (`X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, `X-Shopify-Api-Version`) in the HMAC-signable string in `Request#to_signable_string`, or otherwise cryptographically bind them to the body before `Registry.process` treats them as trusted tenant/event identity, so that the same validated HMAC cannot be replayed under a different shop or topic.

### Proof of Concept
1. Attacker installs the target public app on shop `attacker.myshopify.com`; Shopify sends a genuine webhook with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `HMAC_secret(B)`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the identical `raw_body = B` and `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` builds a request whose `to_signable_string` is still `B`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC_secret(B)` and compares to `H` via `OpenSSL.secure_compare` — it matches, so validation passes: [5](#0-4) 
5. `Registry.process` calls the handler with `shop: "victim.myshopify.com"` even though the payload never originated from, nor was signed in relation to, that shop: [6](#0-5)

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
