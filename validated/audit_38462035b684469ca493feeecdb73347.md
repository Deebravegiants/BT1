### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value that is handed to the app's webhook handler is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never included in the HMAC-signed bytes. This breaks the identity binding "shop authenticated == shop the app acts on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body (`@raw_body`), and `Request#hmac` is derived purely from the `hmac-sha256` header value decoded to hex. [1](#0-0) 

`Request#shop` is read independently from the `shop-domain` header and is not part of `to_signable_string`. [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the raw body) and compares it against the received `hmac`. It never checks that the `shop` header is consistent with anything HMAC-signed. After this single check, it forwards `request.shop` straight into `WebhookMetadata`, which is delivered to the app's handler as the authenticated shop identity. [3](#0-2) [4](#0-3) 

Because only the body is signed, an attacker who legitimately receives one valid `(raw_body, hmac)` pair for their own shop (e.g., by installing the app on their own store and letting Shopify deliver a real webhook to their endpoint, or by capturing/replaying any webhook whose body content is attacker-controllable, such as an `app/uninstalled` payload) can resend that exact `raw_body` + `hmac` to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a victim shop. `HmacValidator.validate` only checks the body/HMAC pair — which is unmodified and therefore still valid — and never verifies the header-derived `shop` against anything cryptographically bound. The handler then receives `WebhookMetadata` claiming to be for the victim shop while nothing about the request actually originated from, or was signed for, the victim shop.

This is the equality that breaks: `shop authenticated (bytes covered by HMAC) != shop acted upon (request.shop header, handed to the app as trusted identity)`.

### Impact Explanation
Apps built on this gem are documented to trust `WebhookMetadata#shop` as the authenticated tenant identifier for routing webhook side effects (e.g., updating per-shop state, deleting shop data on `shop/redact`, disabling features, billing changes) without additional verification, since the library's own `process` method is the sole authentication gate before handler dispatch. An attacker who can obtain any one valid signed webhook body (trivially, by owning a development/trial shop that installs the app) can then impersonate a victim shop's webhook delivery to trigger the app's cross-tenant webhook handler logic — this is a cross-tenant access primitive stemming purely from this gem's own authentication implementation.

### Likelihood Explanation
Likelihood is limited by the fact that the attacker needs to control or capture a `(raw_body, hmac)` pair that is meaningful/exploitable for the target handler logic (e.g., a webhook whose body content doesn't need to reference a specific shop, such as certain mandatory compliance topics or shop-agnostic topics), and needs network access to the app's public webhook endpoint. No credentials, `api_secret_key`, or access tokens are required — only the ability to install the app on any shop (including the attacker's own) to receive one legitimately signed webhook body.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header value inside the signed material, or otherwise cryptographically bind the header-derived shop to the HMAC-verified payload before it is trusted. Minimally, `Utils::HmacValidator` should validate the full set of Shopify webhook headers together with the body, or `Request#to_signable_string` should incorporate the `shop` (and other identity-bearing headers) so that a mismatch between the signed body and the asserted shop is detected and rejected.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com` and capture a real webhook delivery to the app's public webhook endpoint, recording the raw body and the `x-shopify-hmac-sha256` header value.
2. Replay the exact same request to the app's webhook endpoint, keeping the raw body and `x-shopify-hmac-sha256` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the (unmodified) raw body and succeeds. [5](#0-4) 
4. `request.shop` returns `"victim.myshopify.com"` from the forged header and is passed into `WebhookMetadata`, delivered to the app's handler as an authenticated event for the victim shop. [2](#0-1)

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-192)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler
```
