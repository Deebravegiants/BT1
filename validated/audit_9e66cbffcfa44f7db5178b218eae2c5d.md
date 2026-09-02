Confirmed: `to_signable_string` for `Webhooks::Request` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`) that are never included in the HMAC-covered string. `Registry.process` validates only the body's HMAC and then forwards the unauthenticated `request.shop` value into the handler as the tenant identifier.

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`) values that the gem hands to the host application's webhook handler are read directly from HTTP headers that are excluded from the signed payload, so the "authenticated" identity (proven via HMAC with the app's shared `client_secret`) is not bound to the "identified tenant" (`request.shop`) that the handler acts on.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` — which are used by `Registry.process` to route the payload and are passed straight into `WebhookMetadata` for the app's handler — are read from unauthenticated headers, never mixed into the HMAC computation: [3](#0-2) 

`Registry.process` only checks the body HMAC before dispatching to the handler with `request.shop` as the tenant identity: [4](#0-3) 

Because every shop that installs the same app shares the same `client_secret` (`Context.api_secret_key`), the HMAC over a given raw body is identical no matter which shop originated it. This breaks the equality that should hold: `shop authenticated by HMAC == shop acted on by the handler`. In reality, `shop authenticated by HMAC` is undefined (the shop header isn't part of the signed data) while `shop acted on` is taken from a caller-controlled header.

### Impact Explanation
An attacker who can obtain one genuine `(raw_body, hmac)` pair for the app — trivially available by having the app installed on their own (attacker-controlled) shop and capturing their own legitimate webhook delivery — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `Registry.process` will accept the HMAC as valid (since it only covers the body) and hand `WebhookMetadata.new(shop: <victim domain>, ...)` to the host application's handler, causing the app to process/attribute data under the wrong tenant. This is a cross-tenant identity confusion in a security-critical control (webhook authenticity/tenant binding), matching the "cross-tenant access" impact class.

### Likelihood Explanation
Any developer/merchant who can install the app (an unprivileged internet user, not requiring `api_secret_key`, an access token, or any privileged account) can capture one authentic webhook body+HMAC pair from their own shop and reuse it against the shared endpoint with a forged shop header, since nothing in the library ties the HMAC to the shop identity. No credential theft, TLS interception, or social engineering is required — only observation of the library's documented `Registry.process`/`Webhooks::Request` contract.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the value verified by HMAC, or otherwise cryptographically tie the shop header to the signed body — e.g., look up the expected shop for a given HMAC/session out of band, or include the shop domain in the signable string used for verification (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signed parameters). At minimum, document to consumers that `request.shop` from `Webhooks::Request` is unauthenticated and must not be trusted as a tenant identifier without additional verification (e.g., matching it against a `shop` value obtained from an independently verified session/OAuth record).

### Proof of Concept
1. Install the target app on attacker's own shop `attacker-shop.myshopify.com`; capture a legitimate webhook delivery — e.g. `orders/create` with body `{"id":1}` and header `x-shopify-hmac-sha256: <valid-hmac-of-body>` (computed by Shopify using the shared `client_secret`).
2. Replay the exact same raw body and the exact same `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` — [2](#0-1)  — so validation succeeds despite the forged shop header.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: {"id":1}, ...)` — [5](#0-4)  — and the host application processes/stores data under the victim's tenant based solely on the unauthenticated header.

### Citations

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
