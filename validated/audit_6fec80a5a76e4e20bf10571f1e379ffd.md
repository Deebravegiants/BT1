### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook relabeling - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which only signs `request.to_signable_string` (the raw body). The `shop` (from `shopify-shop-domain`/`x-shopify-shop-domain` header) is never included in the signed material, yet it is trusted as the tenant identifier passed to every registered handler.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it with the `hmac` field using `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated headers: [2](#0-1) 

`Registry.process` uses this unvalidated header value directly as the tenant identifier passed to the app's handler: [3](#0-2) 

This exactly matches the audited bug class: "a field acted on but not covered by the HMAC." Here, the equality that should hold is:
`shop used to identify the tenant in WebhookMetadata == shop cryptographically bound to the signed payload`
but in fact the gem only proves `HMAC(body, client_secret) == received_hmac`; it proves nothing about which shop that body belongs to.

Because the app's `client_secret` (used as the HMAC key) is shared across *all* shops that have installed the app — not shop-specific — an attacker who controls their own shop installation of the target app receives real, validly-signed webhook deliveries from Shopify for their own store. The attacker can capture such a request (same `raw_body`, therefore an unchanged, still-valid HMAC) and replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and optionally `topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` dispatches to the handler with `shop: request.shop` set to the attacker-chosen victim domain, exactly following the gem's documented API (`docs/usage/webhooks.md` instructs handlers to key all downstream logic off `data.shop`).

### Impact Explanation
Any first-party logic that keys per-tenant actions off `WebhookMetadata#shop` (session lookup/invalidation, `app/uninstalled` cleanup, GDPR data requests, billing state changes, order/customer data ingestion) can be triggered for a shop the attacker does not own, using only a webhook payload originating from the attacker's own (or any) shop installation. This is a cross-tenant boundary violation caused entirely by this gem's `HmacValidator`/`Webhooks::Request` design, satisfying the "cross-tenant access" criterion for High impact, since the shop-authentication binding the gem is supposed to enforce for tenant dispatch is absent.

### Likelihood Explanation
The only requirement is an unprivileged internet user who has installed the app on any shop (including a free/trial shop they control) so they can capture one validly-signed webhook, then replay it against the app's public webhook endpoint with a forged `shopify-shop-domain` header. No access token, `client_secret`, or privileged account is needed — this is directly reachable from the public webhook route documented in `docs/usage/webhooks.md`.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the shop domain to the webhook payload before dispatch (e.g., cross-check the header shop domain against an out-of-band verified value, or require the host app to corroborate `data.shop` against its own webhook subscription records keyed by delivery ID looked up via the Admin API rather than trusting the header verbatim).

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook event (e.g. `orders/create`) to receive a real Shopify-signed delivery: headers `shopify-hmac-sha256: <valid HMAC over body>`, `shopify-shop-domain: attacker.myshopify.com`, plus `raw_body`.
2. Replay the exact same `raw_body` to the app's webhook endpoint, changing only the header:
   `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged header as `request.shop`. [4](#0-3) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only covers `raw_body`, which is unchanged. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to act on behalf of the victim shop despite the request never having been authenticated for that tenant. [6](#0-5)

### Citations

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
