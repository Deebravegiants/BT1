Confirmed. The vulnerability is a real, reachable identity-binding gap in the webhook processing path.

### Title
Webhook `shop-domain` Header Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing via Replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value that identifies *which tenant* the webhook belongs to is taken from an HTTP header that is never included in the signed material. Because the app's `api_secret_key` is shared across every shop that installs the app, any actor who can obtain one validly-signed webhook (e.g., by installing the app on their own store and triggering an event) can replay that exact body+HMAC pair while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header for an arbitrary victim shop domain. The library accepts this as a fully valid, verified webhook and hands the attacker-controlled `shop` value straight to the registered handler.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body: [2](#0-1) 

Meanwhile `Request#shop` is read straight from an attacker-suppliable HTTP header with no cryptographic tie to the HMAC or to any other verified value: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards `request.shop` unchanged to the app's handler: [4](#0-3) 

The equality the gem should guarantee is:
`shop_the_HMAC_was_computed_for == shop_delivered_to_the_handler`

Because `api_secret_key` is a single shared secret per app (not per shop), a valid `(raw_body, hmac)` pair generated for the attacker's own shop remains valid for *any* `shop-domain` header value — the signature check has no way to detect the substitution since the shop field was never part of the signed bytes. This breaks the binding between "bytes verified" (body) and "identity acted on" (shop header), letting an unprivileged app-installer forge webhooks that appear to originate from a different merchant's store.

### Impact Explanation
This is a cross-tenant data-integrity/authentication issue: a handler that trusts `WebhookMetadata#shop` to route or persist Shopify-originated data (order updates, GDPR redaction requests, inventory changes, uninstall/app-lifecycle events, etc.) can be made to apply attacker-supplied data to a victim shop's tenant record, since the request passes all verification the gem performs. This satisfies the "cross-tenant access" criterion — the confidentiality/integrity boundary between merchants is crossed using only what any developer with an installed instance of the app (an unprivileged internet user relative to other tenants) can obtain.

### Likelihood Explanation
Any user who can install the app on a store they control (a public app install, or a free/dev store) can trigger a webhook to capture a legitimate `(body, hmac)` pair, then simply resend it with a different `shop-domain`/`x-shopify-shop-domain` header value. No access to `api_secret_key`, access tokens, or any privileged credential is required — only the ability to author raw HTTP requests to the app's public webhook endpoint, which is exactly the scenario this gem is meant to guard against.

### Recommendation
Bind the shop identity to the verified request instead of trusting the header in isolation:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header in the HMAC-signable material, or
- Require the caller (host application) to cross-check `request.shop` against the shop of the session/webhook subscription that was registered for that `webhook_id`/topic before invoking the handler, and have `Registry.process` enforce this rather than leaving it as an undocumented responsibility, or
- At minimum, document prominently in `Registry.process` that `shop` is unauthenticated data and must be independently verified by callers against their own installed-shop records before being trusted for tenant routing.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook event (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sent (both computed with the app's single shared `api_secret_key`).
2. Attacker replays the exact same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets:
   `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — it matches `H`, so the request is accepted: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)`, indistinguishable from a genuine webhook for the victim shop: [6](#0-5)

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
