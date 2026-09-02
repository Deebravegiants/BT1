### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` attribute that is read directly from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature used to authenticate the webhook only covers the raw request body. Anyone who can produce a validly-signed body (e.g., a merchant who legitimately installed the app and receives genuine webhook deliveries) can replay that body to the app's webhook endpoint while substituting an arbitrary `shop` header, and `Registry.process` will accept it and hand the forged shop identity to the app's `WebhookHandler`.

### Finding Description
The HMAC binding is defined in `to_signable_string`, which returns only the raw body: [1](#0-0) 

The `shop` (and `topic`, `api_version`, `webhook_id`) values are pulled straight from HTTP headers, which are not part of the signed data: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `to_signable_string`, i.e., only the body bytes — never the shop header: [3](#0-2) 

`Registry.process` performs exactly this check, then immediately trusts `request.shop` as the tenant identifier passed into the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` const with no independent verification — it is exactly what was in the (unauthenticated) header: [5](#0-4) 

This is a direct analog of the reported bug class: the `shop` field is *acted on* (used as the tenant/session key by the host application's handler) but is *not covered by the HMAC* that is supposed to authenticate the whole request. The binding that should hold — "the shop the HMAC authenticates" == "the shop the handler operates on" — is broken because the HMAC only authenticates the body, not the header claiming which shop it came from.

### Impact Explanation
Any unprivileged actor who can obtain one genuinely-HMAC-signed webhook body for shop A (trivial: install the app as shop A and let Shopify deliver any webhook, then capture body+HMAC) can resend that exact body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to victim shop B. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will dispatch to the handler with `shop: "B"`. Any host application that keys its persistence, session lookup, or business logic (e.g., data deletion for `shop/redact`, subscription state changes, order processing) off `WebhookMetadata#shop` will act on shop B's data/tenant context using attacker-controlled, replayed content — a cross-tenant access/write primitive achievable by any internet user with no access token, no `client_secret`, and no privileged account, satisfying the Critical cross-tenant-access bar.

### Likelihood Explanation
Likelihood is high for a determined attacker: obtaining one valid signed webhook body only requires installing the target app as any shop (a normal, unprivileged action) or observing traffic from any app that logs/echoes webhook bodies. No secret material is needed to forge the header itself, since headers are entirely attacker-controlled at the HTTP layer and are not part of the signed payload.

### Recommendation
Include the `shop` (and ideally `topic`/`api_version`/`webhook_id`) values in the signable string, or otherwise cryptographically bind them to the HMAC, e.g.:
```ruby
def to_signable_string
  "#{shop}|#{topic}|#{@raw_body}"
end
```
and update `compute_signature`/validation accordingly, or require the host application to independently verify that `request.shop` matches session data already trusted for that access token, rather than trusting a bare header value gated only by a body-only HMAC.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to (e.g., `app/uninstalled`), capturing the raw JSON body and the genuine `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Replay an HTTP POST to the app's webhook endpoint with:
   - Body: the exact captured raw body (unchanged, so the HMAC remains valid)
   - Header `X-Shopify-Hmac-Sha256`: the exact captured HMAC (unchanged)
   - Header `X-Shopify-Shop-Domain`: `victim.myshopify.com` (changed)
   - Header `X-Shopify-Topic`: unchanged (or any registered topic)
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the forged header: [2](#0-1) 
4. `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC: [6](#0-5) 
5. The registered `WebhookHandler#handle` is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload/HMAC only ever proved authenticity for `attacker.myshopify.com`'s webhook — the app now processes attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
