## Title
Webhook `shop` (and `topic`/`webhook-id`) identity is not covered by the HMAC signature, allowing cross-tenant webhook impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by checking `Utils::HmacValidator.validate(request)`, but the HMAC signature covers only the raw request body, not the `shop-domain` (or `topic`/`webhook-id`) header that identifies which tenant the event belongs to. An unprivileged attacker who possesses one valid `(raw_body, hmac)` pair delivered by Shopify to the app (trivially obtainable by installing the app on their own free/dev shop and capturing the webhook it receives) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header value. The signature check still passes because it only re-computes the HMAC over `@raw_body`, so the request is accepted and dispatched to the host app's handler as if it originated from the spoofed shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` value, also taken from a header: [3](#0-2) 

`Registry.process` gates only on this body-HMAC check, then immediately hands the header-derived, unauthenticated `request.shop` to the host app's handler as the tenant identity for the event: [4](#0-3) 

The binding that is broken is: **`shop` value verified by the signature check** (none — it's not part of the signed bytes) **≠ `shop` value trusted and forwarded as the event's tenant identity** (`WebhookMetadata#shop`, taken directly from the `shop-domain` header). Because the HMAC only proves "this body byte-sequence was signed by Shopify with the app secret," and not "this body was signed *for this specific shop domain*," an attacker can freely re-attribute a previously-observed, validly-signed webhook body to any shop domain string of their choosing.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler receives `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` and will typically use `shop` to look up the tenant's session/access token or to write tenant-scoped data (e.g., mark shop X's order as fulfilled, disable shop X's subscription, etc.), while the `body` content actually reflects shop A's data. An attacker who legitimately received one webhook (e.g., by installing the app themselves) can forge that exact request under any other shop's domain, causing the host application — built entirely on top of this gem's supported webhook-processing API — to apply shop-A's webhook data/state transition under an attacker-chosen shop identity. This satisfies the "cross-tenant access" Critical impact category, since no access token, session, or `api_secret_key` is required by the attacker — the attacker just needs to have received exactly one legitimate webhook delivery, and can replay it with an arbitrary shop header.

### Likelihood Explanation
Likelihood is high for any app that accepts self-serve installs (very common for Shopify apps), since obtaining a valid `(raw_body, hmac)` pair only requires installing the app on the attacker's own store and capturing any webhook. No secret key or privileged access is needed; the exploit only requires the ability to send arbitrary HTTP requests to the app's webhook endpoint with attacker-controlled headers, which is standard unauthenticated internet access.

### Recommendation
Include the identity-binding fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind the shop domain to the signed payload (e.g., derive/verify the shop against a registered per-shop signing verification, not solely header content). At minimum, `Request#to_signable_string` should not authenticate the body in isolation while `topic`/`shop` continue to be trusted unauthenticated header values for dispatch decisions.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify.
2. Attacker crafts a new POST request to the app's webhook endpoint with the exact same raw body and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `@raw_body` — the mismatched shop is irrelevant to the check: [5](#0-4) 
4. The handler executes with `shop: "victim-shop.myshopify.com"` and the attacker's captured order body, causing the host application to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
