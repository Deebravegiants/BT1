### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature only covers the raw request body. Because Shopify webhook HMACs are computed with the app's single `client_secret` shared across every shop that installs the app (not a per-shop key), any shop that installs the app can obtain a validly-signed webhook body and then replay it with the shop-domain header changed to point at a different, victim shop. `Registry.process` passes this unauthenticated `shop` value straight to the handler, so the app will process attacker-controlled data believing it came from the victim tenant.

### Finding Description
The equality this code is supposed to enforce is:
`HMAC(secret, bytes_verified) == HMAC(secret, bytes_acted_on)`, where `bytes_acted_on` must include everything the handler treats as authoritative, in particular the tenant identity (`shop`).

In `lib/shopify_api/webhooks/request.rb`, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` (and `topic`, `webhook_id`, `api_version`) are pulled from headers that are outside the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (the body) against the HMAC — it never binds the header-derived `shop`: [3](#0-2) 

`Registry.process` validates only that HMAC-over-body check, then forwards the unauthenticated `request.shop` to the handler as the tenant identity for the event: [4](#0-3) 

Since Shopify computes webhook HMACs using the app's `client_secret`, which is identical for every shop that installs the app, a validly-signed body obtained from webhooks delivered for shop A can be replayed to the app's webhook endpoint with the `shop-domain` header rewritten to shop B. The HMAC check still passes (it only checks the body bytes), and the handler executes with `data.shop == "B"` even though the body content actually originated from shop A. This breaks the binding between the authenticated bytes (body) and the identity the application acts on (shop), letting an attacker who controls a shop's app installation inject attacker-chosen webhook payloads under another tenant's identity.

### Impact Explanation
This is a cross-tenant identity-binding break: the `shop` value that host applications use to select the tenant's session/store/data (as demonstrated in `WebhookMetadata.new(topic:, shop:, body:, ...)`) is attacker-controllable data that never participates in the HMAC. A malicious merchant who has the app installed on their own store can forge webhook deliveries that the host application will attribute to a different, victim merchant, achieving cross-tenant access/injection without needing the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must be able to trigger a real, Shopify-signed webhook delivery for some shop (e.g., by installing the app on their own store and generating events with attacker-chosen body content), then replay/proxy that request to the app's webhook endpoint with a modified shop-domain header. This is fully achievable by any unprivileged user who can install the app, requires no leaked secret, TLS interception, or privileged access — only observation/replay of the app's own inbound webhook traffic.

### Recommendation
Bind the tenant identity into the verified material instead of trusting an out-of-band header:
- Include the `shop` (and ideally `topic`/`webhook_id`) in the signable string, or independently verify that the `shop-domain` header corresponds to a shop for which the app holds a valid, previously-established session/access token before processing the webhook.
- Alternatively, look up and validate the shop against the app's known installed-shops list before dispatching to the handler, rather than trusting the header value unconditionally.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook event (e.g., `orders/create`) with attacker-crafted order data; Shopify signs the body with the app's shared `client_secret`.
2. Attacker intercepts/replays this exact HTTP request to the app's webhook endpoint but changes the `x-shopify-shop-domain` header to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body)`; since the body is unchanged, validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, processing it as if it were a legitimate event from the victim tenant.

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
