This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers via `shopify_header`.### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is trusted from unauthenticated HTTP headers, not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` field that is later handed to app-level `WebhookHandler#handle` as `WebhookMetadata.shop` is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is not part of the signed payload. Any caller who can produce one valid `(body, hmac)` pair for the app's shared `api_secret_key` can replay that exact body/hmac pair while substituting an arbitrary `shop-domain` header, and `Utils::HmacValidator.validate` will still report success.

### Finding Description
`Registry.process` gates webhook processing solely on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body — `shop`, `topic`, `webhook_id`, and `api_version` are pulled independently from HTTP headers via `shopify_header`, and are never included in the string that gets HMAC-verified: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop asserted by the HMAC-covered payload == shop attributed to the event in WebhookMetadata`. That binding is broken because the HMAC only proves "this body was produced with the app's `api_secret_key`" — it says nothing about which shop the header claims to be from. Since a Shopify app uses a single shared `client_secret`/`api_secret_key` across all installed shops (there is no per-shop signing key in this gem or in Shopify's webhook design), any legitimate merchant who has installed the app can capture a genuine `(raw_body, hmac)` pair from their own store's webhook deliveries and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to point at a different (victim) shop. `HmacValidator.validate` will pass because it never re-derives or checks `shop` against the signature, and the resulting `WebhookMetadata` (used by `Registry.process` to dispatch to the handler) will report the forged `shop`: [5](#0-4) [6](#0-5) 

This is consistent with the report's bug class: "a field acted on but not covered by the HMAC" — here the field is `shop`, which downstream handler code will almost certainly use as a tenant identifier (to look up sessions, update per-shop state, etc.), creating a cross-tenant confusion.

### Impact Explanation
Any app built on this gem that trusts `WebhookMetadata.shop` as an authenticated tenant identifier (a very natural and common usage pattern, since the gem's own `WebhookMetadata` struct presents `shop` alongside `body` as if both were equally trustworthy) is exposed to cross-tenant webhook spoofing: an attacker who is a legitimate merchant of the app (or otherwise obtains one valid signed webhook body, e.g., for a shop-independent/generic topic) can cause the app to process an event and attribute it to an arbitrary victim shop domain, without needing that victim's credentials. Depending on what the handler does with `data.shop` (e.g., mandatory `shop/redact`, `customers/redact`, `app/uninstalled` processing, cache invalidation, deprovisioning), this can result in cross-tenant data manipulation, denial of service against another tenant's account state, or forged compliance/redaction actions attributed to the wrong shop — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only:
1. Attacker access to at least one genuinely-signed webhook body/hmac pair — trivially obtainable by installing the app themselves (a legitimate, unprivileged action any internet user can take on their own store) and capturing their own store's webhook delivery.
2. The ability to POST an arbitrary HTTP request with custom headers to the app's public webhook receiver endpoint — this is the intended, unauthenticated entry point for Shopify webhooks, so no credential or privileged access is needed to reach it.

No `api_secret_key`, access token, or TLS interception is required by the attacker; only knowledge of a legitimately-obtained sample of their own signed traffic. Likelihood is limited primarily by whether the payload of the topic being replayed happens to be generically useful for spoofing an event with a different shop attribution (e.g., topics whose body doesn't intrinsically reference the originating shop, such as `app/uninstalled`), but the core signature-binding weakness itself is unconditional.

### Recommendation
Include the asserted `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise bind them cryptographically to the signed body, so that `Utils::HmacValidator.validate` fails if any header used for tenant attribution has been altered relative to what Shopify actually signed. At minimum, update `Webhooks::Request#to_signable_string` to incorporate the `shop` header (matching Shopify's actual signing scheme if it does bind shop, or otherwise requiring apps to cross-check `shop` against a known/expected value, e.g., an active session's shop) before dispatching to `WebhookHandler#handle`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger a webhook whose body content does not depend on identifying information (e.g., `app/uninstalled`), and capture the raw POST: headers `x-shopify-hmac-sha256: <H>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: app/uninstalled`, and raw body `B`.
2. Replay the exact same request to the app's webhook endpoint, but change only the `x-shopify-shop-domain` header to `victim.myshopify.com`, keeping body `B` and hmac `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate(request)` calls `compute_signature(request.to_signable_string, secret)` which only hashes `B`, so it matches `H` and returns `true`: [7](#0-6) 
4. `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, causing the app to process an `app/uninstalled` (or other) event as if it originated from the victim shop, even though the victim never sent or authorized it.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
