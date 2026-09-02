### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body, then unconditionally trusts the `shop-domain` (and `topic`, `webhook-id`, `api-version`) HTTP headers to attribute the payload to a tenant. Because the HMAC only signs the body — never the shop-identifying header — and the signing secret (`Context.api_secret_key`) is a single app-wide secret shared by every shop that installs the app, any shop that can obtain one valid `(body, hmac)` pair for its own tenant can replay that exact body/HMAC pair while spoofing the `shop-domain` header to impersonate a different, victim tenant.

### Finding Description
The webhook authenticity check is implemented as: [1](#0-0) 

`shop` is read directly from `shopify_header("shop-domain")`, while `to_signable_string` — the value that actually gets HMAC-verified — is only `@raw_body`. The `hmac` itself is also taken from a header (`hmac-sha256`), not derived from or bound to the `shop` header in any way.

`HmacValidator.validate` confirms only that the body was HMAC'd with the app's secret: [2](#0-1) 

`Registry.process` performs exactly this check and then passes the unauthenticated `request.shop` straight into the handler metadata used by the host application to attribute the event to a tenant: [3](#0-2) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop attributed to the webhook handler`

In this implementation, the left side does not exist at all — the HMAC never covers the shop (or topic/webhook-id) fields, so the equality is vacuously false: the shop used downstream is whatever value an attacker places in the header, constrained only by needing *some* valid `(body, hmac)` pair signed with the app's single, cross-tenant secret.

Since `Context.api_secret_key` is one value per app (not per shop) — as evidenced by `HmacValidator` taking only `Context.api_secret_key`/`Context.old_api_secret_key` with no shop parameter, and by `AuthQuery`/`JwtPayload` using the same singular secret across all shops — any tenant that has legitimately installed the app can trigger a real webhook delivery to itself (e.g. `orders/create`, `customers/data_request`, `shop/redact`, `app/uninstalled`) and thereby obtain a body+HMAC pair valid under the shared secret. That attacker-tenant can then POST the identical body and HMAC to the app's public webhook endpoint while substituting the victim's `x-shopify-shop-domain` header. `Registry.process` will accept it as authentic and invoke the handler with `shop: <victim-shop>`, causing the host application's per-tenant business logic (data deletion for mandatory GDPR topics, order/customer state changes, uninstall cleanup, etc.) to run against the wrong tenant's data.

### Impact Explanation
This breaks tenant isolation (cross-tenant access) purely through header spoofing by another unprivileged app-installing user, without needing the merchant's access token, the app's `client_secret`, or any credential beyond what any installer of the app already has. Depending on which topic is replayed, the impact ranges from data corruption to triggering mandatory-compliance webhooks (`shop/redact`, `customers/redact`) against a shop that never requested them, i.e., cross-tenant data manipulation/exfiltration entirely mediated by this gem's webhook verification API.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate installer of the target app on one's own store (an "unprivileged" relationship relative to other tenants of the same app), (2) triggering a real webhook to capture a valid `(raw_body, hmac)` pair from one's own shop, and (3) sending an HTTP POST to the app's public webhook endpoint with the captured body/HMAC and a forged `x-shopify-shop-domain` header. No secret material or victim credentials are needed, and the gem's `Registry.process`/`Request` classes provide no additional binding between the authenticated bytes and the shop attribution, making this straightforward for any moderately capable app user to attempt.

### Recommendation
Do not treat header-derived `shop`, `topic`, `webhook-id`, or `api-version` as authenticated. At minimum, require host applications (and provide gem-level support) to cross-check `request.shop` against an expected/known shop for the delivery context (e.g. a per-shop webhook secret or a shop allow-list keyed by installation), or extend the signable string in `Request#to_signable_string` to include the header fields that are acted upon (topic, shop-domain, webhook-id) so the HMAC actually binds them, mirroring the fix pattern in the referenced report where the acted-upon value was brought under the same tracked/verified scope as the authorization check.

### Proof of Concept
1. App has two tenants: Attacker-Shop (`attacker.myshopify.com`) and Victim-Shop (`victim.myshopify.com`), both installed on the same app instance (same `Context.api_secret_key`).
2. Attacker triggers a real webhook on their own store (e.g. creates an order), causing Shopify to POST to the app's webhook endpoint with:
   - body: `{"id":123,...}`
   - header `x-shopify-hmac-sha256`: `Base64(HMAC-SHA256(secret, body))`
   - header `x-shopify-shop-domain`: `attacker.myshopify.com`
3. Attacker captures `(body, hmac)` (e.g. via their own server logs, or since they control the receiving endpoint if the app is self-hosted/testable, or via a subscribed pub/sub protocol they can read).
4. Attacker replays the identical `body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `body` against `hmac` — both unchanged from the original valid delivery.
6. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, and the host application processes the attacker's order-creation payload as if it belonged to `victim.myshopify.com`. [4](#0-3) [5](#0-4)

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
