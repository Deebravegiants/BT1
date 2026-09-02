### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook-id`, and `api-version` values — which are taken directly from HTTP headers and passed on to the application's `WebhookHandler` as trusted tenant/context identifiers — are never included in the HMAC-signed payload. This breaks the intended binding between "bytes verified" and "bytes acted on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates only this HMAC-over-body and then forwards the unauthenticated `shop` header value straight into `WebhookMetadata`, which app code uses to identify the tenant the webhook is "for": [3](#0-2) [4](#0-3) 

By contrast, in the OAuth flow the library does correctly bind `shop` (and other fields) into the HMAC-signed string: [5](#0-4) 

This confirms the library's own security model intends for identity-relevant fields to be part of the signed data — but the webhook path fails to do so for `shop`.

Because Shopify apps use a single, static `api_secret_key` shared across *all* installed shops to sign webhooks, any attacker who installs the app on their own (attacker-controlled) shop can legitimately receive a validly-HMAC-signed webhook for an arbitrary topic/body. The equality the system should enforce is:
`shop header value == shop that produced the HMAC-signed bytes`
But the actual verified equality is only:
`HMAC(raw_body, secret) == received_hmac`
with `shop` completely absent from that computation. The attacker can therefore replace the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with any victim shop domain while keeping the same valid HMAC and body, and `Registry.process` will accept it and hand the forged `shop` to the app's handler as if it were an authentic message about the victim tenant.

### Impact Explanation
This crosses a tenant boundary: an app using this gem's webhook facilities has no way, using the library's guarantees, to be sure the `shop` value in `WebhookMetadata` actually corresponds to the shop that produced the payload/HMAC. Any downstream logic that keys off `data.shop` (e.g., looking up the shop's session/access token, writing to per-shop records, billing, GDPR/compliance webhook processing) can be manipulated to act on/behalf of a shop the attacker does not control — a cross-tenant data confusion primitive with a Critical classification per the target impact list.

### Likelihood Explanation
Exploitation requires only being able to install the app on some (even a free-tier) shop, which is an attacker-accessible, unprivileged action, and then replaying an intercepted/self-generated webhook request with a modified header — no access to the app's `api_secret_key` or any victim credentials is required, since the header is not part of what's verified.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value covered by the HMAC computation (or otherwise cryptographically bind them), matching the pattern already used in `AuthQuery#to_signable_string`. At minimum, `shop` must be part of the signed bytes before `Registry.process` trusts it and forwards it to `WebhookHandler#handle`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, obtaining genuine webhook deliveries (e.g., `app/uninstalled`) with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`.
2. Attacker captures one such request: `raw_body = '{"id":1}'`, `hmac = <valid>`.
3. Attacker resends this exact `raw_body`/`hmac` pair to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in [6](#0-5)  passes because it only checks `to_signable_string` (`raw_body`), which is unchanged.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though the payload never originated from Shopify on behalf of `victim.myshopify.com`.

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
