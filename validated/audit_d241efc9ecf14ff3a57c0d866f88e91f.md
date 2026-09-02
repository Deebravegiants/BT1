### Title
Webhook Shop-Domain Spoofing via HMAC Field Exclusion Enables Cross-Tenant Data Misattribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the webhook HMAC signature only to the raw request body, while the `shop` value used to route and attribute webhook data to a tenant is read from an unrelated, unsigned HTTP header. Because the app's webhook secret (`api_secret_key`) is shared across every shop that has the app installed, any shop that legitimately receives a signed webhook can replay that exact body+signature pair while forging the `shopify-shop-domain` header to point at a different, victim shop. `ShopifyAPI::Webhooks::Registry.process` accepts the request as valid and dispatches the handler with the attacker-forged shop, breaking the tenant identity binding.

### Finding Description
The equality that should hold is: `shop claimed in the request == shop the HMAC signature is computed over`. In this gem it does not hold.

`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read from a separate, independently-controlled header, with no cryptographic tie to the body or hmac: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` only ever computes/compares the signature against `to_signable_string` (i.e. the raw body) — the shop field never enters the signed message: [4](#0-3) 

`Registry.process` validates only that HMAC, then dispatches the handler with `request.shop` taken as trusted tenant identity: [5](#0-4) 

Since `api_secret_key` is one shared secret for the whole app (not per-shop), a legitimately signed webhook from Shop A's own store (which the attacker fully controls, e.g. their own free/dev shop that has the app installed) is a **valid** `(raw_body, hmac)` pair under the app's secret. The attacker can capture this pair and re-POST it to the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to name a victim shop. `HmacValidator.validate` recomputes HMAC over the same raw body and it matches — validation succeeds — yet `WebhookMetadata.shop` returned to the handler is the forged victim shop.

This is the analog of the reported bug class: the check ("is this HMAC valid") is decoupled from the field actually acted upon by the application logic (`shop`), i.e. a field acted on but not covered by the HMAC — precisely mirroring the report's checks-effects-interactions/binding-break class, here manifesting as an authentication-vs-attribution mismatch instead of a re-entrancy TOCTOU, but breaking the same kind of identity equality.

### Impact Explanation
Any application built on this gem that trusts `WebhookMetadata#shop` (returned by `Registry.process`) to select which tenant's data/session/state to update is exposed to cross-tenant data injection/corruption: an attacker-controlled shop can inject arbitrary webhook payloads (order data, app-uninstalled, customer data, etc., limited to topics the app is registered for) that the host application will process as if they came from a different, victim shop. This satisfies the "Critical - cross-tenant access" impact class, since data crosses a tenant boundary purely due to the header/hmac field mismatch, requiring no access token, secret, or privileged account — only a shop the attacker themselves controls with the app installed (an unprivileged, ordinary flow available to any internet user who installs a public app on a free dev store).

### Likelihood Explanation
Likelihood is high for any app that (a) is public/multi-tenant, (b) has webhooks registered, and (c) uses `shop` from `WebhookMetadata` to key data. All of this is normal, encouraged gem usage (`docs/usage/webhooks.md`; `Registry.process`). Capturing a valid `(body, hmac)` pair from your own store and replaying it with a different header requires no cryptographic secret and no special privilege — just control of an ordinary shop install.

### Recommendation
Include the shop domain (and other Shopify-supplied identifying headers relied upon by consumers, e.g. `webhook-id`, `api-version`) in the signable message used for HMAC verification, or independently verify that the claimed `shop` corresponds to a shop for which the app currently holds/expects a session before dispatching the webhook to handlers. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked against a known/installed shop list by the host application before use.

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com`.
2. Shopify sends a legitimately HMAC-signed webhook (e.g. `orders/create`) to the app for `attacker.myshopify.com`; attacker captures the raw POST body and the `x-shopify-hmac-sha256` header value.
3. Attacker replays the identical body and hmac header to the app's webhook endpoint, but overwrites `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the hmac against the raw body — this still matches the app's shared `api_secret_key`, so validation succeeds.
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)` and the host application processes/stores attacker-controlled data under the victim shop's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
