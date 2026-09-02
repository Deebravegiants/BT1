### Title
Webhook shop domain and topic are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` and passed to the app's handler are read from HTTP headers that are never included in that signed content. Any party that can obtain one valid `(body, hmac)` pair signed with the app's shared secret can replay that pair to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` (and `topic`/`webhook-id`) header, and the HMAC check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from attacker-controllable HTTP headers: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which in turn calls `validate_signature`, hashing only `to_signable_string` (i.e., the body) with the app's `api_secret_key`: [3](#0-2) [4](#0-3) 

After the HMAC check succeeds, `process` forwards `request.shop` (and `request.topic`, `request.webhook_id`) untouched to the app's handler as `WebhookMetadata`: [5](#0-4) 

The binding that should hold is: `shop header == shop that produced this HMAC-signed body`. Because the HMAC only covers the raw body, that equality is never checked — the `shop` (and `topic`/`webhook_id`) header is a field "acted on but not covered by the HMAC". Any actor who has legitimately received one real webhook for their own shop (i.e., merely installed the app on a shop they control — an unprivileged action, no `api_secret_key` or access token needed) possesses a valid `(body, hmac)` pair signed with the app's secret. They can then POST that exact body/HMAC pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for an arbitrary victim shop domain (and swap `topic`/`webhook-id` too). `HmacValidator.validate` still returns `true` because it only re-hashes the body, and the forged `shop` value is handed to the host app's handler as if Shopify itself attested to it.

### Impact Explanation
Downstream apps rely on `data.shop` from `WebhookMetadata` to determine which tenant/shop a webhook event applies to (e.g., looking up that shop's session/access token, writing data keyed by shop, or triggering shop-scoped side effects such as data deletion for GDPR webhooks). Because the shop attribution is forgeable independent of the signed payload, an attacker who legitimately installed the app on one shop can cause the host application to process arbitrary attacker-chosen webhook bodies under a different shop's identity — a cross-tenant identity binding break directly enabled by this gem's verification logic.

### Likelihood Explanation
The prerequisite (installing the target app on a shop the attacker controls, or simply capturing/replaying one legitimate webhook) is trivially available to any developer/merchant who can install the app — no leaked secrets or privileged access required. Forging the `x-shopify-shop-domain`/`topic`/`webhook-id` headers on a direct POST to the public webhook callback URL requires no cryptographic material at all, since these fields are outside the signed content.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise bind the shop domain) into the HMAC-signed content, or independently verify `request.shop` against a value derived from an authenticated source (e.g., cross-check against the registered webhook subscription) before dispatching to handlers in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a real webhook, e.g. `orders/create`, to the app's callback endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures that `(B, HMAC)` pair (their own traffic to their own endpoint).
3. Attacker sends a new POST to the same app webhook endpoint with the identical body `B` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally changes `x-shopify-topic`/`x-shopify-webhook-id`).
4. `Utils::HmacValidator.validate` re-computes the HMAC over `B` only (via `to_signable_string`), matches the supplied signature, and returns `true`. [6](#0-5) 
5. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`, `body: parsed(B)`, even though this webhook never originated for that shop. [7](#0-6)

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
