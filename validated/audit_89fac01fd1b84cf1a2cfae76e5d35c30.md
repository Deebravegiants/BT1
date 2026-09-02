### Title
Webhook shop-domain and topic identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and attribute the webhook are read from unauthenticated HTTP headers. This breaks the intended identity binding `hmac == HMAC(shop, topic, body)` down to `hmac == HMAC(body)`, letting an attacker who possesses any one valid `(raw_body, hmac)` pair replay it with a forged `shop-domain`/`topic` header and have it accepted as an authentic webhook for an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` (all header-derived) to build the `WebhookMetadata` handed to the app's registered handler: [3](#0-2) 

`HmacValidator.validate` confirms this: it signs/verifies `verifiable_query.to_signable_string`, which for webhooks is body-only, never the shop or topic headers: [4](#0-3) 

The identity-binding equality that should hold is `hmac == HMAC_secret(shop ++ topic ++ body)`, so that the shop the handler is told the event came from is cryptographically tied to the signature. What the gem actually implements is `hmac == HMAC_secret(body)`, with `shop`/`topic` supplied out-of-band via headers that are never mixed into the signable string. This is the same bug class as the referenced `felt_to_bytes_little` finding: a value (`shop`/`topic`) that is acted upon downstream is not covered by the verification check that is supposed to bind it, so an attacker can substitute an arbitrary value for it as long as the covered portion (the body) still validates.

### Impact Explanation
Any actor who can obtain one legitimate `(raw_body, x-shopify-hmac-sha256)` pair for the target app (e.g., by installing the app on their own free/dev Shopify store and capturing a webhook Shopify sends them — this requires no access token, no `api_secret_key`, and no privileged account) can replay that exact body+hmac to the app's public webhook endpoint while spoofing the `x-shopify-shop-domain` header to name a different, victim shop, and optionally the `x-shopify-topic` header to select a different registered handler. Because `Registry.process` only checks the HMAC over the body, the forged request passes validation, and the handler receives `WebhookMetadata.shop` equal to the attacker-chosen victim domain. Depending on how the host application's handler uses `metadata.shop` (typically to look up the tenant/session or to act on stored per-shop data — e.g., mandatory GDPR webhooks like `customers/redact` or `shop/redact`, or `app/uninstalled`), this allows an unauthenticated actor to inject fabricated events attributed to a different merchant's tenant, i.e., cross-tenant access/action without holding any credential for that tenant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The webhook endpoint is by design public and unauthenticated apart from the HMAC check, so no credentials, TLS interception, or social engineering are needed. The only requirement is possessing one valid `(body, hmac)` pair for the app, which any user can trivially obtain by installing the app on a store they control (a normal, unprivileged action) and capturing the webhook Shopify delivers to them. Because the body itself is not required to reference any shop (webhook bodies for topics like `app/uninstalled` or `customers/redact` carry minimal, attacker-influenced-at-signup content), replay with a spoofed shop header is straightforward. Likelihood is high for apps that dispatch handler logic keyed on `metadata.shop` from the registry without independent verification.

### Recommendation
Bind the shop domain and topic into the signed content that `HmacValidator` verifies, e.g., include `shop-domain` and `topic` (and ideally `webhook-id`, `api-version`) in `Request#to_signable_string` (mirroring Shopify's actual webhook signing scheme if it already covers more than the body, or at minimum re-deriving/cross-checking these headers against an independently trusted source), and reject any request where the header-provided shop/topic cannot be cryptographically tied to the verified payload before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a store they control) and configures a webhook subscription for a topic the app has registered a handler for (e.g., `customers/redact`).
2. Shopify delivers a legitimate webhook to the app: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's real `api_secret_key`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` (trivial, since it's their own store/webhook delivery).
4. Attacker replays an HTTP POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...spoofed shop...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(B)` against `H`, per `lib/shopify_api/utils/hmac_validator.rb` and `Request#to_signable_string` returning only `@raw_body`.
6. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed B, ...)`, causing the app to treat the request as an authentic event for `victim-shop.myshopify.com` despite it never having sent this webhook.

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
