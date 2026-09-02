### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the tenant identifier (`shop`) that the library hands to the application's webhook handler is taken from an unauthenticated HTTP header. Anyone who can obtain one legitimately-signed webhook delivery (e.g. by installing the app on their own free/dev store) can replay that exact body+HMAC pair while swapping the `shop-domain` header to point at a victim shop, and `Registry.process` will accept it as valid and dispatch it as if it came from the victim.

### Finding Description
`Utils::HmacValidator.validate` is called on the `Request` object in `Registry.process`: [1](#0-0) 

The validator recomputes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

For webhook requests, `to_signable_string` returns **only the raw body** — it does not include `shop`, `topic`, or any other header: [3](#0-2) 

Meanwhile, the `shop` value that is trusted and forwarded to the app's business logic is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the signed body at all: [4](#0-3) 

This is precisely the identity-binding break the analog looks for: **bytes verified (the raw body) ≠ bytes/field acted on (the `shop-domain` header)**. `Registry.process` passes this unauthenticated `request.shop` value directly into the `WebhookMetadata` object delivered to the app's handler: [1](#0-0) 

Because `shop` is outside the signed payload, an attacker does not need the app's `client_secret` or any victim credential to forge the tenant binding — they only need one authentic `(raw_body, hmac)` pair, which they can freely obtain from Shopify by installing the target app on any shop they control (e.g. a free developer store) and capturing a real webhook delivery for a topic of interest (e.g. `shop/redact`, `app/uninstalled`, `orders/create`). They then resend the identical body and HMAC to the app's webhook endpoint with the `shop-domain` header changed to the victim's `*.myshopify.com` domain. `HmacValidator.validate` still passes because it only checks the body, and the handler receives `shop: <victim-shop>` as if the event genuinely originated from the victim.

### Impact Explanation
This breaks the equality `shop_bound_by_hmac == shop_used_by_handler` — an attacker fully controls the right-hand side while the left-hand side is empty (no shop coverage at all). This enables cross-tenant impersonation of webhook events: an app relying on `WebhookMetadata#shop` (as returned by this gem, and as documented for building handlers) to scope database writes, revoke access, or process mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) can be tricked into performing tenant-scoped side effects against a shop the attacker does not operate. This matches the Critical "cross-tenant access" impact bucket, since the attacker is crossing the tenant boundary using only their own (unprivileged) installation of the app.

### Likelihood Explanation
Likelihood is high for any app that is publicly installable: obtaining one legitimate signed webhook only requires installing the app on a free/dev store, and the replay itself is a single unauthenticated HTTP POST with a modified header — no secret material, TLS interception, or social engineering is required.

### Recommendation
Bind the `shop` (and ideally `topic`, `api-version`, `webhook-id`) values into the signable string, or otherwise cryptographically bind the header-derived identity to the payload, e.g. Shopify's HMAC always covers the raw body over TLS from the platform, so the gem should additionally verify that the `shop-domain` header is consistent with metadata that can be re-derived/cross-checked (or document/require callers to independently verify the shop against an active session/installation record) before trusting `request.shop` for any tenant-scoped action. At minimum, update `Webhooks::Request#to_signable_string` so it cannot be satisfied by a body+hmac pair captured for a different shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers/receives a real webhook delivery for topic `X`, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header (validly signed by Shopify with the app's real secret).
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` returns only `raw_body`, unchanged from step 1.
4. The handler receives `WebhookMetadata.new(topic: "X", shop: "victim-shop.myshopify.com", body: ..., ...)`, and the host app processes the event as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
