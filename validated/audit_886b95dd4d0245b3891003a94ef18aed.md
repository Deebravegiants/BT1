### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity is taken from unauthenticated HTTP headers, not from the HMAC-covered bytes - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and other dispatch fields entirely from HTTP headers, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator.validate` only covers the raw request body. This breaks the intended binding `verified_bytes == acted_on_identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/verifies the HMAC solely against that signable string [2](#0-1) . However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never part of the signed bytes [3](#0-2) .

`Webhooks::Registry.process` validates the HMAC over the body and then, without any additional check that the header-derived `shop` matches an installed/known shop, immediately hands `request.shop` to the app's handler as trusted tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

Because the app's `client_secret` is used only to authenticate the body bytes, an attacker who can produce a valid HMAC for a given body (e.g., by replaying/observing a legitimately signed webhook body for their own shop, or by triggering webhooks from a shop they control that has the same JSON body shape as another tenant's event) can freely set the `shopify-shop-domain` header to a different (victim) shop domain while keeping the HMAC valid, since the header is not part of what's signed. This equality that should hold — `hmac_verifies(bytes) == identity_bound(bytes)` — does not hold here: `hmac_verifies(raw_body)` is true, but the `shop` used for dispatch is an independent, unauthenticated field.

### Impact Explanation
Apps that use `WebhookMetadata#shop` from `Registry.process` to select which tenant's stored access token/session to act on (a documented, expected usage pattern for this gem's webhook API) can be tricked into misattributing a validly-HMAC'd payload to an arbitrary victim shop. This is a cross-tenant identity-binding gap at the library boundary: the gem asserts the webhook is "valid" (HMAC ok) and hands over a `shop` value the caller reasonably treats as authenticated, but the library itself never binds that `shop` field to the signature.

### Likelihood Explanation
Exploitability depends on the attacker's ability to obtain a body/HMAC pair that verifies (e.g., by being a legitimate merchant of their own shop who receives real webhooks from Shopify, or by finding a body whose JSON shape is shop-domain-independent, such as an `app/uninstalled` payload with generic content) and then replaying it toward the app's webhook endpoint with a forged `shopify-shop-domain` header. This requires the app's webhook endpoint to be reachable and the attacker to control or observe a validly-signed payload, which is achievable by any merchant who has installed the app (a low-privilege position, not requiring `api_secret_key`, tokens, or TLS interception).

### Recommendation
Include `shop`, `topic`, `webhook-id`, and `api-version` in the HMAC-signed material (or otherwise bind them to the body, e.g. by requiring the caller to pass the expected shop and comparing it against a shop already known/authenticated by the host application) so that `to_signable_string` cannot verify successfully unless the header-derived identity fields match what was actually signed by Shopify.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook whose body content does not reveal shop-specific data (e.g. a generic `app/uninstalled` payload `{}`), together with its valid `x-shopify-hmac-sha256` value computed over that body with the app's shared secret.
2. Attacker replays the exact same raw body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-hashes `@raw_body` [1](#0-0)  and succeeds because the body is untouched.
4. The handler executes with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", ...)` [5](#0-4) , causing the host app to act (e.g., invalidate/rotate/delete stored session data) for a shop the attacker does not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
