I have sufficient evidence to build the finding on the webhook shop-domain/HMAC binding break.

### Title
Webhook `shop-domain` Header Excluded From HMAC Coverage Enables Cross-Tenant Data Injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value passed to webhook handlers directly from the unauthenticated `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) HTTP header, while `ShopifyAPI::Utils::HmacValidator` only verifies the HMAC over the raw request body. The identity binding `shop authenticated == shop stored/acted on` is broken: the cryptographic signature never covers the shop-domain header, so an attacker who can obtain any one valid `(body, hmac)` pair for the app (e.g., by installing the same public app on their own store and capturing a genuine webhook delivery) can replay that exact body/HMAC pair while substituting an arbitrary victim shop's domain in the header, and the gem will accept it as valid and hand the victim shop identity to the host application's webhook handler together with attacker-controlled body content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the (unsigned) header: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e. the body) and compares it with the `hmac` value, never incorporating `shop`: [3](#0-2) 

`Registry.process` checks only this body-only HMAC before dispatching to the handler with the header-derived, unauthenticated shop value: [4](#0-3) 

Crucially, the webhook HMAC secret (`Context.api_secret_key`) is the app's single shared secret — the same key is used for every shop that has installed the app — not a per-shop secret. So a `(raw_body, hmac)` pair that is valid for shop A's webhook is *also* a valid signature for the exact same body when replayed with the `shop-domain` header changed to shop B, because the signature never bound the shop identity to the body in the first place. This is exactly the pattern called out in the prompt's rules: "a field acted on but not covered by the HMAC" / "a shop authenticated versus the shop stored as a session key."

Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` IS included in `to_signable_string` and therefore is properly bound by the HMAC: [5](#0-4) 

That the webhook path lacks the equivalent binding is the root cause.

### Impact Explanation
Any application built on this gem that uses the `shop` field from `WebhookMetadata` to select a merchant tenant/session context (a documented, intended use — see `Registry.process` constructing `WebhookMetadata.new(... shop: request.shop ...)`) can be tricked into applying attacker-supplied webhook body content under a different, victim merchant's identity. This is a cross-tenant confusion: data ostensibly "from shop B" that the handler processes (e.g., updating records, triggering GDPR/redaction flows, billing/inventory changes) actually originates from attacker-controlled shop A. Because the mandatory topics `shop/redact`, `customers/redact`, and `customers/data_request` are handled through this exact code path, an attacker-shop could forge a data-request/redact payload attributed to an arbitrary victim domain. This satisfies the Critical bar of "cross-tenant access."

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the same (public) app on a shop they control — an unprivileged-internet-user-level action for any publicly listed app — capture one legitimate webhook delivery (body + `X-Shopify-Hmac-Sha256`), and replay it to the app's webhook endpoint with a modified `X-Shopify-Shop-Domain`/`x-shopify-shop-domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is needed.

### Recommendation
Bind the shop identity into the webhook signature verification path, or otherwise refuse to trust the `shop-domain` header unless the caller independently confirms that the domain in question matches shop metadata Shopify includes in the signed body (where available), or maintain and check the returned `shop` value against an app's own known-installed-shops list before treating it as authoritative. At minimum, document prominently that `request.shop` is not covered by the HMAC and must not be trusted as an authenticated identity by host applications, and consider deriving/validating shop identity via a channel that is actually covered by the signature (e.g., requiring hosts to cross-check `webhook_id`/topic against records tied to the session that registered the webhook).

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com`, granting scopes and receiving a genuine webhook delivery for a registered topic, e.g. `orders/create`:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: ...
   Body: {"id":1,"note":"malicious payload"}
   ```
2. Attacker captures the exact `Body` and `X-Shopify-Hmac-Sha256` value (both are visible to them since it was delivered to their own server).
3. Attacker replays the identical body and HMAC header to the app's webhook endpoint, changing only the shop-domain header:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-for-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: ...
   Body: {"id":1,"note":"malicious payload"}
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate` re-computes HMAC over `raw_body` only [6](#0-5)  and it matches, since `shop` was never part of the signed content.
5. `Registry.process` dispatches to the app's handler with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and the attacker's body [7](#0-6) , causing the host application to process attacker-controlled content as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
