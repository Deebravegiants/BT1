### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the shop identity (`shop-domain` header) is read separately and never included in the signed bytes. `Registry.process` validates only the body's HMAC and then dispatches the shop value taken from the unauthenticated header to the app's webhook handler, breaking the binding between "bytes verified" and "shop acted upon."

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery`'s HMAC by recomputing the signature over `to_signable_string` and comparing it to the supplied `hmac`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw body (`@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are parsed from HTTP headers that are completely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC of the request object (i.e., of the body only) and then immediately trusts `request.shop` — a header value never bound by that signature — to construct the metadata passed to the app's registered handler: [3](#0-2) 

Because Shopify's webhook HMAC secret (`api_secret_key`) is shared across all shops that installed the same app, an attacker who installs the app on their own store receives genuine webhook deliveries with valid `X-Shopify-Hmac-Sha256` signatures computed over the JSON body. Since the header carrying the shop identity is not part of the signed bytes, the attacker can replay that exact `body` + `hmac` pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) with any victim shop's domain. `HmacValidator.validate` will still return `true`, because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

This is exactly the "bytes verified vs. bytes parsed" / "field acted on but not covered by the HMAC" identity-binding break: the equality the code implicitly assumes,
`hmac_signed_bytes == identity_bytes_acted_upon`,
does not hold, since `hmac_signed_bytes = raw_body` while `identity_bytes_acted_upon = headers["shop-domain"]`.

### Impact Explanation
Any application that uses the `shop` field of `WebhookMetadata` to select a tenant context (look up a session/access token, attribute the payload to a particular merchant, or gate multi-tenant data) can be tricked into associating attacker-controlled webhook data with a victim shop identifier. This is a cross-tenant integrity/confidentiality issue: data that is fully attacker-controlled (both body content and forged shop attribution) is processed under another tenant's identity, satisfying the "cross-tenant access" criterion for Critical severity. The vulnerability lives entirely in this gem's `Webhooks::Request`/`Registry` code, not in host application misuse of a documented contract, since the API explicitly exposes `shop` as if it were authenticated the same way the topic/body are.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-controlled development/free store to receive a legitimately signed webhook (trivial, no privileged credentials needed), and (2) replaying that request with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — this fits the unprivileged-internet-user threat model exactly. Likelihood is Medium-High since it is a low-effort replay attack.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the verified payload before it is trusted:
```diff
 def to_signable_string
-  @raw_body
+  "#{shop}\n#{@raw_body}"
 end
```
Alternatively, require that `shop` be cross-checked against an already-authenticated session/store record (e.g., a shop known to have installed the app with the same secret) before acting on webhook data, rather than trusting the header value provided by the caller.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) so Shopify sends:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - Body: attacker-controlled JSON (attacker fully controls order details on their own store).
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual, and `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks `@raw_body`, which is unchanged: [4](#0-3) 
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is `"victim-shop.myshopify.com"`, even though the payload is entirely attacker-authored: [5](#0-4)

### Citations

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
