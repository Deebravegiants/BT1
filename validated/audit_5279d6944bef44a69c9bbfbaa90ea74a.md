### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `topic`, `shop`, `api_version`, and `webhook_id` from raw HTTP headers, but the HMAC signature that `ShopifyAPI::Utils::HmacValidator.validate` checks is computed only over the raw request body (`to_signable_string` returns `@raw_body`). None of the identifying headers — most importantly `shop` — are bound into the signed value, yet `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` unconditionally once the body HMAC checks out and hands it to the host app's handler as the tenant identifier.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only this body-HMAC, then immediately trusts `request.shop`/`request.topic` to build the tenant-identifying `WebhookMetadata` passed to the app's handler: [3](#0-2) 

This reproduces the report's bug class ("field acted on but not covered by the HMAC" / shop-identity mismatch): the equality the gem should enforce is
`hmac == HMAC(secret, raw_body ‖ shop ‖ topic ‖ ...)`,
but the gem actually enforces only
`hmac == HMAC(secret, raw_body)`.

Because the app's `client_secret` is shared across every shop that installs the app (it's a single per-app secret, not per-shop), any merchant that has installed the app can generate a validly-signed webhook body for their own shop (e.g. by triggering any subscribed event, such as `orders/create`), then replay that exact `raw_body` + `hmac-sha256` header pair while substituting the `shop-domain` header for a different (victim) shop that also has the app installed. `HmacValidator.validate` still succeeds because it never inspects the shop header, and `Registry.process` will call the app's handler with `shop: <victim-shop>` and the attacker-controlled body — the host application has no way, using this library's API, to detect that the shop identity was substituted.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on `ShopifyAPI::Webhooks::Registry.process`/`WebhookMetadata` to provide. An attacker who legitimately installs the app on their own store can attribute forged, attacker-controlled webhook payloads to any other shop's identifier that also has the app installed, letting them inject or corrupt data the host app persists keyed by `shop` (cross-tenant data pollution / cross-tenant access), which matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate merchant/tenant of the app (no leaked secrets, no privileged account, no TLS interception) — they can obtain one validly-signed webhook for their own shop through ordinary use of the app and then modify the `shop-domain` (and optionally `topic`/`webhook-id`) header when replaying it to the app's webhook endpoint. The gem provides no defense against this because it only signs the body.

### Recommendation
Include the identifying headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind the shop identity to the signature (e.g., verify the shop against a previously stored per-shop signing context) so that swapping the `shop-domain` header invalidates the signature. At minimum, document that `Registry.process` callers must independently corroborate `request.shop` against a known, previously authenticated shop before trusting it, since this library does not do so today.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`.
2. Attacker triggers a webhook-eligible event on their own shop, capturing the raw POST body `B` and its valid `X-Shopify-Hmac-Sha256` header `H = HMAC(client_secret, B)`.
3. Attacker replays a request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(client_secret, B) == H`, per [4](#0-3)  and [5](#0-4) .
5. `Registry.process` invokes the app handler with `shop: "victim.myshopify.com"` and the attacker's body, per [3](#0-2) , causing the host application to process attacker data under the victim's tenant identity.

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
