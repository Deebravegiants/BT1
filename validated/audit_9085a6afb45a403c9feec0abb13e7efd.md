Based on my investigation, I found a concrete instance of the flagged bug class: **a field acted upon by the library but not covered by the HMAC signature** — matching the required analog pattern.### Title
Webhook shop-domain/topic/webhook-id identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, but the HMAC only signs the raw request body. The `shop`, `topic`, and `webhook_id` values — read from HTTP headers — are never included in the signed bytes, yet they are trusted and handed to the host application's handler as authoritative identity for the tenant/event.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from HTTP headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the received signature: [3](#0-2) 

`Registry.process` then trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the verified bytes — and forwards them to the host application's webhook handler as the authenticated identity of the event: [4](#0-3) 

The broken identity binding, expressed as an equality that the code fails to enforce:
`bytes_verified_by_hmac (raw_body) != identity_fields_acted_on (shop, topic, webhook_id)`.

Because the HMAC key (`Context.api_secret_key`) is the app's single client secret shared across **every** shop that has installed the app — not a per-shop secret — any tenant that has legitimately installed the app can capture one of its own valid `(raw_body, hmac)` pairs (e.g. from a real webhook it received, such as `app/uninstalled` or `customers/data_request`). That tenant can then replay the exact same body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a **different, victim shop**. `HmacValidator.validate` still returns `true` because it only checks the (unmodified) body against the shared secret, and `Registry.process` dispatches the forged event to the handler with `shop: "victim-shop.myshopify.com"`.

### Impact Explanation
This breaks tenant isolation (Critical - cross-tenant access): a host application that keys per-shop side effects off `WebhookMetadata#shop` (e.g., deactivating/deleting a shop's stored session or access token on `app/uninstalled`, processing GDPR `shop/redact` or `customers/data_request` deletions, or triggering shop-scoped business logic) can be made to apply another merchant's legitimate, signed webhook body to an arbitrary victim shop of the attacker's choosing, purely by manipulating unauthenticated headers. This is a genuine cross-tenant boundary violation caused entirely by this gem's verification logic, not by the host ignoring documented behavior — the gem itself asserts HMAC validity (`Errors::InvalidWebhookError` is not raised) for a request whose acted-upon identity fields were never authenticated.

### Likelihood Explanation
Likelihood is realistic but requires the attacker to be an app-installing tenant (an "unprivileged internet user" relative to other merchants of the same app, satisfying the "unprivileged internet user" threat model) who can capture one authentic `(body, hmac)` pair from their own shop — trivial to do by installing the app and observing an incoming webhook (e.g. via a public endpoint/logging proxy they control). No access to `api_secret_key`, access tokens, or the app's other merchants' credentials is required.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed/verified material, or independently bind them to a value the gem can authenticate (e.g., require the host to look up an existing session for `request.shop` and fail closed if none exists) before dispatching to the handler. At minimum, document and enforce that `WebhookMetadata#shop` must never be trusted as tenant-authenticated unless cross-checked against a known/installed shop record, and consider deriving `shop` from the HMAC-covered payload body (most Shopify webhook payloads contain shop-identifying data) rather than solely from headers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and captures a legitimate webhook delivery, e.g. an `app/uninstalled` POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`).
2. Attacker replays the identical body `B` and header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, forges `X-Shopify-Topic`/`X-Shopify-Webhook-Id` similarly, since none of these affect the HMAC).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, shown at: [5](#0-4) 
which only re-computes the HMAC over `B` (via `Request#to_signable_string` returning `@raw_body`) and matches `H` — validation passes.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host application performs the shop-scoped side effect (e.g., deletes stored session/token, processes redaction) against `victim-shop.myshopify.com`, even though the actual authenticated payload originated from `attacker-shop.myshopify.com`.

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
