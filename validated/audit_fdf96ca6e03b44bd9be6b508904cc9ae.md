This confirms the design: `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which computes the HMAC over `to_signable_string` — i.e., `@raw_body` only [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values are all read directly from unauthenticated HTTP headers and are never included in the signed bytes [2](#0-1) . `Registry.process` then hands `request.shop` straight to the host app's handler as the tenant identifier, trusting it as if it were verified [3](#0-2) .

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted for tenant identity without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` cryptographically verifies solely the JSON body bytes. The `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers are parsed from the request but never bound into the signed content. `Registry.process` treats `request.shop` as the authenticated tenant identity and forwards it unmodified to the app's `WebhookHandler`.

### Finding Description
The identity binding that should hold is: `shop header == shop cryptographically bound to the HMAC-signed payload`. In this gem it instead holds: `shop header != anything covered by HMAC` — the signature only proves the body bytes were produced with the shared secret; it says nothing about which shop-domain header should accompany that body.
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares against `verifiable_query.hmac` [4](#0-3) .
- For `Webhooks::Request`, `to_signable_string` is exactly `@raw_body`, excluding all headers [1](#0-0) .
- `shop`, `topic`, `webhook_id`, `api_version` are read straight off attacker/network-controlled headers with no cross-check against the signed body [2](#0-1) .
- `Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching `request.shop` to the handler as the trusted tenant key [3](#0-2) .

Because the shop-domain is a field acted on (used as the tenant/session key by the host app) but not covered by the HMAC, anyone capable of producing a validly HMAC'd body/header pair for *any* store they control (e.g., their own shop, or any store where they can trigger a legitimate webhook, which requires no special privilege beyond having their own Shopify dev store) can replay that exact body with a different `shopify-shop-domain` header. Since the signature only covers the raw body, the forged request still validates, and the library reports it as originating from the attacker-chosen shop.

### Impact Explanation
If a host application (using this gem per its documented contract) keys any per-tenant state — e.g., "which shop just got this event", data deletion/redaction routing for `shop/redact`, `customers/redact`, GDPR requests, or order/inventory sync — off `WebhookMetadata#shop`, an attacker can cause cross-tenant data confusion: injecting events attributed to a victim shop domain using a validly-signed body captured from their own store's webhook deliveries. This breaks the tenant isolation boundary the HMAC is supposed to enforce, matching the "cross-tenant access" impact category, since the `shop` field is the only identity binding used downstream and it is unauthenticated.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one valid `(raw_body, hmac)` pair signed with the app's real secret. This is achievable without any stolen credentials: any unprivileged internet user can create their own free Shopify development store, install the target app, and trigger genuine webhook deliveries for topics with attacker-influenceable bodies (e.g., `app/uninstalled`, `shop/redact`), then replay the intercepted (or self-observed, since webhooks arrive at their own publicly reachable app endpoint) request while swapping only the `shopify-shop-domain` header to a victim shop. No `api_secret_key`, access token, or privileged account for the victim shop is needed.

### Recommendation
Bind the header values into the signed content, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC before trusting them. Concretely, extend `to_signable_string` (or add a secondary check) to include the shop-domain/topic/webhook-id alongside the body — mirroring the OAuth `AuthQuery#to_signable_string`, which already signs `shop`, `host`, `state`, etc. [5](#0-4)  — so `HmacValidator.validate` fails whenever the header-carried identity fields disagree with what was actually signed by Shopify for that delivery.

### Proof of Concept
1. Attacker creates their own Shopify dev store `attacker.myshopify.com` and installs the target app (no special privilege required).
2. Attacker triggers a webhook whose body they can influence or simply observe (e.g., `app/uninstalled`), capturing the delivered `raw_body` and the corresponding `shopify-hmac-sha256` header — both valid under the app's real secret.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body`/`hmac` but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `Registry.process` [6](#0-5)  passes because it only checks the body bytes.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , and any host-app logic keyed on `shop` (deletion, sync, notification) executes against the victim tenant using attacker-controlled body content.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
