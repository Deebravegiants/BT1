### Title
Webhook HMAC only covers the request body, not the `shop`/`topic`/`webhook_id` headers, allowing cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values used to route and label the webhook come straight from HTTP headers and are never included in the signed material [2](#0-1) . Because the identity of the tenant (`shop`) and the semantic meaning of the payload (`topic`) are "bytes parsed" but not "bytes verified", anyone who can obtain one genuine, HMAC-signed webhook body (e.g. a merchant receiving webhooks for their own store) can replay that same body+hmac pair while swapping the `shop-domain`, `topic`, or `webhook-id` headers, and the signature check still succeeds.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the received signature [3](#0-2) . For webhooks, `to_signable_string` returns only `@raw_body`, deliberately excluding all headers [4](#0-3) .

`Registry.process` uses this same `request` object both to authenticate ("Invalid webhook HMAC" check) and to dispatch:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [5](#0-4) 

`request.shop` and `request.topic` are read verbatim from the `shopify-shop-domain` / `shopify-topic` headers [6](#0-5) . Since the HMAC never covers these header values, the equality that the gem implicitly relies on — "the shop/topic the HMAC proves this body came from" == "the shop/topic acted upon by the handler" — does not hold. An attacker who legitimately receives one valid `(raw_body, hmac)` pair for their own shop (all merchants installing the app receive genuine, correctly-signed webhooks for their own store) can POST that unchanged `(raw_body, hmac)` pair to the app's webhook endpoint while substituting arbitrary `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` header values. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will dispatch the (attacker-chosen) handler with a `WebhookMetadata` claiming an arbitrary victim `shop` and topic.

### Impact Explanation
This breaks the tenant-identity binding the report's bug-class describes: a field (`shop`) that is acted upon by the application but not covered by the HMAC that is supposed to authenticate the request. Depending on what the host app's webhook handlers do (e.g. mandatory GDPR `shop/redact`/`customers/redact` handlers, `app/uninstalled` cleanup that revokes/deletes stored sessions, billing state changes), this allows a low-privileged merchant to trigger tenant-scoped side effects attributed to a different shop than the one that actually generated the request — a cross-tenant action performed without any credential belonging to the victim shop. This matches the Critical/High category of cross-tenant access enabled purely through this gem's own webhook-verification logic, with no dependency on the host app "ignoring documented API" since the gem itself only authenticates the body.

### Likelihood Explanation
Exploitation requires only (a) being a merchant with the app installed on any single shop, so as to legitimately receive one valid webhook body+hmac pair from Shopify, and (b) being able to POST directly to the app's public webhook endpoint with custom headers — no access token, `api_secret_key`, or other victim credential is needed. This is a realistic capability for any unprivileged internet user who can install a public app on a shop they control.

### Recommendation
Include the tenant/topic identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed payload used for verification, or otherwise cryptographically bind them to the body-derived HMAC before trusting `request.shop`/`request.topic` for routing/dispatch in `Registry.process`. At minimum, document prominently that `request.shop` is not authenticated and must not be used as a tenant key without an independent lookup (e.g., verifying the webhook actually corresponds to a shop with a currently valid stored session), and add a check comparing `request.shop` against session/tenant records before invoking handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify send a real webhook (e.g. `orders/create`) to the app's webhook endpoint. Attacker captures the raw request: body `B`, and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` computed with the app's secret) along with `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-webhook-id: <id>`.
2. Attacker replays the exact same body `B` and `x-shopify-hmac-sha256: H`, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` and/or `x-shopify-topic` to a sensitive topic the app also handles (e.g. `app/uninstalled`, `shop/redact`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [1](#0-0) ; since validation only hashes `@raw_body` [4](#0-3) , it returns `true` even though `shop`/`topic` were changed.
4. The registered handler for the (attacker-chosen) topic is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, causing the app to perform tenant-scoped logic (session/data mutation) attributed to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L11-38)
```ruby
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
