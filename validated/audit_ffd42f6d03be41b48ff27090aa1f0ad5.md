I have enough evidence to finalize the analog. The core root cause is confirmed: `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb`) signs only `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers and never enter the HMAC computation. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb`) validates only that body-HMAC and then forwards the header-derived `shop`/`topic` straight to the app's handler as trusted identity metadata.

### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, and `ShopifyAPI::Utils::HmacValidator` verifies the received `X-Shopify-Hmac-Sha256` against that body-only string. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are the fields the host application uses to decide *which tenant and which action* the webhook applies to, are taken from HTTP headers that are entirely outside the HMAC's protected scope.

### Finding Description [1](#0-0) 
`to_signable_string` returns `@raw_body` verbatim, with no inclusion of the shop domain, topic, or any other header. [2](#0-1) 
Yet `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from `shopify_header(...)`, i.e., attacker-controllable HTTP headers. [3](#0-2)  confirms the HMAC comparison is computed purely from `verifiable_query.to_signable_string` (the raw body) against the shared secret — headers never participate. [4](#0-3) 
`Registry.process` validates only this body-HMAC, then immediately trusts `request.topic` and `request.shop` to build `WebhookMetadata` that is handed to the app's handler — the binding "HMAC(body) is valid" is treated as if it also proved "this event belongs to `request.shop`/`request.topic`", which it does not.

Equality that should hold but doesn't: `HMAC-covered bytes == bytes that determine tenant/action identity`. In this gem, `HMAC-covered bytes = raw_body` while `tenant/action identity = headers (shop, topic, webhook_id, api_version)` — two disjoint sets.

### Impact Explanation
Any party that legitimately receives one authentic webhook delivery for their own shop (which they can, simply by running the receiving endpoint for an app they installed — no `api_secret_key` needed) obtains a `(raw_body, valid HMAC)` pair signed with the app's real secret. Because the header set is unauthenticated, that same `(raw_body, hmac)` pair can be replayed to the app's shared webhook endpoint with a different `x-shopify-shop-domain` and/or `x-shopify-topic` header. `Registry.process` will accept it as valid (the body-HMAC still matches) and dispatch it to the handler labeled as belonging to a different shop or a different (potentially higher-trust) topic, e.g., relabeling an ordinary `orders/create` payload as `customers/redact` or `app/uninstalled` for an arbitrary target shop domain the attacker names in the header. This is a cross-tenant identity binding break carried entirely by data the requester controls, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires no possession of `api_secret_key`, no TLS interception, and no privileged account — only the ability to run/observe an app's own webhook receiver (something every merchant who installs the app can do) and then re-POST the captured payload with modified headers to the same publicly reachable webhook endpoint. This is a realistic, low-effort action for any unprivileged app-installing user.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`) in the signable string that is HMAC-verified, or otherwise cryptographically bind them to the body (e.g., verify `shop`/`topic` against a value independently looked up via a trusted API call keyed off the webhook_id, rather than trusting the header verbatim). At minimum, document that consuming applications must not treat `request.shop`/`request.topic` as authenticated unless they perform their own additional binding check.

### Proof of Concept
1. App merchant M installs the app and receives a real webhook: body `B`, headers `x-shopify-shop-domain: m.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H` (H = HMAC-SHA256(secret, B)).
2. M crafts a new HTTP POST to the same webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` and/or `x-shopify-topic: customers/redact`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H == HMAC(secret, B)` — this still passes.
4. The handler registered for `customers/redact` (or whichever topic was substituted) is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "customers/redact", body: parsed_body, ...)`, causing the app to act as if Shopify sent that event for `victim.myshopify.com`, even though it never did.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
