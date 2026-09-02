This confirms the vulnerability path. The webhook `to_signable_string` for `Request` is the raw request body only, while `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from HTTP headers without being covered by the HMAC computation.This confirms the design: `HmacValidator.validate` only checks `to_signable_string` (the raw body) against the HMAC — it never authenticates `topic`, `shop`, `api_version`, or `webhook_id`, all of which come straight from HTTP headers.### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from raw HTTP headers, but `to_signable_string` — the value actually authenticated by `Utils::HmacValidator` — is only the raw request body. The `shop` field that is later trusted and dispatched to app-specific webhook handlers is never bound to the HMAC signature.

### Finding Description
`Registry.process` authenticates an inbound webhook solely via: [1](#0-0) 

This calls `Utils::HmacValidator.validate(request)`, which computes the HMAC over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from headers, completely outside the signed material: [4](#0-3) 

After the HMAC check passes, `request.shop` (header-derived, unauthenticated) is handed to the app's handler as the tenant identifier: [5](#0-4) 

The identity binding that should hold is: `HMAC-authenticated bytes == bytes the handler trusts as the shop`. Here, `to_signable_string == raw_body` while `request.shop` comes from `x-shopify-shop-domain`/`shopify-shop-domain`, so the equality is broken — the shop attribution is never covered by the signature.

Because a single app typically uses one shared `client_secret` (and therefore one shared `api_secret_key`/HMAC key) across every merchant that installs it, an HMAC computed over a given body is valid for that body regardless of which shop domain header accompanies it. An attacker who controls or has previously observed one valid `(body, hmac)` pair from a webhook belonging to their own shop (a legitimate, unprivileged installer of the target app) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` will still succeed, because it never inspects the shop header, and the app's handler will process the webhook as if it originated from the victim's shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: the shop identity dispatched to app handlers is attacker-controllable even though the payload signature is valid. Depending on how a host application's `WebhookHandler` uses `data.shop` (e.g., to look up/mutate per-shop records, trigger shop-scoped side effects, or attribute mandatory GDPR webhooks like `customers/redact`/`shop/redact`), this enables cross-tenant data confusion/corruption using another (attacker-controlled) shop's legitimately-signed webhook body. This matches the "Critical — cross-tenant access" impact category, since the shop-authenticated-vs-shop-acted-upon equality is broken with a low-privilege attacker (any merchant who has installed the app and can capture one of their own inbound webhooks).

### Likelihood Explanation
Requires an attacker who has installed the target app on their own shop (or otherwise can capture a legitimately delivered webhook + its valid HMAC for a known body) and can then re-POST that same body/HMAC pair to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key` or any Shopify-internal secret is required — only reuse of a signature that is valid for that body under the shared per-app secret. Exploitability further depends on the host app's webhook receiver actually forwarding raw headers/body unmodified to `ShopifyAPI::Webhooks::Request.new`, which is the gem's documented usage pattern.

### Recommendation
Bind the shop identity (and ideally topic/webhook id) into the signed material verified by `HmacValidator`, or require callers to separately verify that the shop in the webhook matches an expected/installed shop before dispatching to handlers. At minimum, document that `request.shop` is unauthenticated and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against a known installed-shop list) prior to handler invocation in `Registry.process`.

### Proof of Concept
1. App A is installed by both a legitimate merchant "attacker.myshopify.com" and a victim "victim.myshopify.com", sharing the same app `client_secret`.
2. Shopify delivers a real webhook to the app for "attacker.myshopify.com" with body `B` and header `x-shopify-hmac-sha256: HMAC(client_secret, B)`.
3. The attacker captures this `(B, HMAC)` pair (trivial, since it is delivered to their own endpoint/logs).
4. The attacker re-sends a POST to the app's webhook endpoint with the same body `B`, the same valid HMAC header, but `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` recomputes HMAC over `B` only, matches, and returns `true`; `Registry.process` invokes the handler with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"`, even though the payload never actually originated from or was signed with knowledge of that shop.

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
