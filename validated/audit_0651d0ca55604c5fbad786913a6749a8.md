### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate(request)` passes, then forwards `request.shop` (taken from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header) to the app's handler as the tenant identifier. Because `Request#to_signable_string` only covers the raw body, the `shop` field is never bound to the HMAC, so any holder of one valid `(raw_body, hmac)` pair can relabel it to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `hmac` and `to_signable_string`: [1](#0-0) 

`to_signable_string` returns only `@raw_body` — the `shop` (and `topic`, `api_version`, `webhook_id`) accessors read directly from HTTP headers and are never included in the signed payload.

`HmacValidator.validate` computes and compares the signature strictly against `to_signable_string`: [2](#0-1) 

`Registry.process`, the gem's own dispatch entry point, relies on this validation and then constructs `WebhookMetadata` using `request.shop` as the trusted tenant identifier passed to the app's handler: [3](#0-2) 

The equality the gem implicitly claims is: `shop used by handler == shop cryptographically bound to the signed body`. In reality it is `shop used by handler == shop header value`, which is attacker-controlled and independent of the HMAC. This mirrors the report's bug class: "a field acted on but not covered by the HMAC."

### Impact Explanation
Any unprivileged internet user who can obtain one legitimate `(raw_body, hmac)` pair (e.g., by installing the app on their own store, a routine and unprivileged action) can replay that exact body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Registry.process` will pass HMAC validation (it only checks the body) and hand the handler a `WebhookMetadata` claiming the event originated from the victim shop. Any host app that uses `WebhookMetadata#shop` to scope data writes, trigger shop-level actions (e.g., GDPR `customers/redact`, `shop/redact` handling), or select which tenant's session/record to update will act on the wrong tenant — a cross-tenant integrity/confidentiality violation performed entirely through data this gem asserts as "HMAC verified."

### Likelihood Explanation
Reaching this requires only: (1) the ability to receive one real webhook for any topic the attacker's own shop can trigger (trivial — install the app, or await a routine background webhook such as `app/uninstalled`), and (2) sending an HTTP POST with attacker-controlled headers to the app's public webhook endpoint, which is unauthenticated by design. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind `shop` (and ideally `topic`/`api_version`/`webhook_id`) into the signable string used for HMAC validation, or otherwise cryptographically tie the header-derived shop to the signed body before exposing it via `WebhookMetadata`. At minimum, document that `Registry.process`'s HMAC check does not authenticate the `shop` header, and require host apps to independently verify shop identity against their own webhook subscription records before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets a webhook fire (or triggers one), capturing the raw POST body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` computed by Shopify over `B` with the app's `client_secret`.
2. Attacker sends a new POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256`: `H` (unchanged)
   - `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (spoofed)
   - `X-Shopify-Topic`: same as original (unchanged, or any topic the app registered)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC purely over `B` and succeeds because `B` and `H` are the original valid pair (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:27-31`).
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the spoofed `victim-shop.myshopify.com` from the header (`lib/shopify_api/webhooks/registry.rb:198-199`), and invokes `handler.handle` with this metadata.
5. The host app's handler processes the payload `B` as an authenticated event for `victim-shop.myshopify.com`, even though nothing tying `B` to that shop was ever verified.

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
