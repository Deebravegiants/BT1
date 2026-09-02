### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is never included in the HMAC-signed payload. `HmacValidator` only verifies the raw request body, so an attacker who legitimately receives a validly-signed webhook for their own shop can replay that same body+signature pair while substituting an arbitrary `shop-domain` header, and the gem will accept it as authentic and hand it to the host application's handler as if it came from the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, deliberately excluding all headers: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it with `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust every other field on the request, including `request.shop`, which is then handed to the app's webhook handler as the tenant identity: [4](#0-3) 

This is the exact identity-binding mismatch described in the report's bug class: the bytes that are cryptographically **verified** (the JSON body) are not the same bytes that are **acted on** for tenant attribution (the `shop-domain` header). Because Shopify apps share a single `api_secret_key` across every shop that installs them, any user who installs the app on their own store receives genuinely HMAC-valid webhooks for their own store's events. That attacker can then resend the identical `(raw_body, hmac)` pair to the app's webhook endpoint while swapping only the `shop-domain` (and optionally `topic`/`webhook-id`) header to name a different, victim shop. `HmacValidator.validate` still returns `true` because it never looked at those headers, and `Registry.process` forwards `shop: <victim-domain>` to the handler.

### Impact Explanation
This breaks the equality that the host application relies on: `shop authenticated by HMAC == shop the webhook data is attributed to`. Any app that uses `WebhookMetadata#shop` to look up per-tenant records, credentials, or state (which is the intended and documented use of the field) can be made to write or process attacker-supplied body content under another merchant's identity — a cross-tenant access/data-injection primitive at the gem layer, even though every check the gem performs "passes."

### Likelihood Explanation
The only prerequisite is that the attacker be able to install the target app on any shop they control (a normal, unprivileged action for a Shopify merchant/developer) so that they receive at least one genuinely-signed webhook body. From there, forging the header swap requires only an HTTP client — no access token, no `api_secret_key`, and no privileged account is required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind them to the signed body (e.g., have `to_signable_string` concatenate the relevant headers with the body before computing/verifying the HMAC), so that the verified bytes and the bytes the application acts on for tenant attribution are always the same input.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g., `orders/create`). They capture the resulting HTTP request: `raw_body` and the `x-shopify-hmac-sha256` header, which is validly computed with the app's shared `api_secret_key` per `lib/shopify_api/utils/hmac_validator.rb`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` — it matches, since the body is unchanged.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` — per `lib/shopify_api/webhooks/registry.rb` lines 198-199 — causing the host application to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
