### Title
Webhook HMAC Only Signs the Raw Body, Not the `shop-domain` Header — Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies its HMAC signature over the raw request body only. The `shop-domain` header — which downstream code treats as the authoritative tenant identifier — is never included in what is signed. Because the app's `api_secret_key` is a single, global secret shared across every merchant that installs the app (not a per-shop secret), any body/HMAC pair that is valid for one shop is also a valid HMAC for the exact same body claimed to originate from a different shop. This breaks the intended binding `hmac == HMAC(secret, body ++ shop)` down to `hmac == HMAC(secret, body)`, letting an attacker who controls one tenant relabel their own legitimately-signed webhook traffic as belonging to a victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers and are not part of the signed material.

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (the body) using the app-wide `Context.api_secret_key`: [2](#0-1) 

`Webhooks::Registry.process` checks only this HMAC, then trusts `request.shop` (and the other unsigned headers) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because `Context.api_secret_key` is a single secret configured for the whole app (not scoped per merchant/shop) — as reflected throughout the auth code, e.g. `Auth::JwtPayload` and `Auth::Oauth` all use the same global `Context.api_secret_key`/`Context.old_api_secret_key` — the same key signs webhook bodies for every installed shop. Consequently:

- Before the attack: `HMAC(secret, body_A)` is valid only in association with shop A's webhook delivery, and the host app's handler is expected to apply `body_A` to shop A's tenant data.
- After the attack: the attacker resends the same `body_A` and the same, still-valid `hmac`, but with the `x-shopify-shop-domain` header changed to shop B. `HmacValidator.validate` still returns `true` because it never looks at the shop header, so `Registry.process` calls the handler with `shop: "shop-B.myshopify.com"` while the (attacker-controlled) `body_A` is applied as if it legitimately came from Shopify for shop B.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the signature authenticates *bytes* (the body) but the application logic (and the host app built on top of this gem) is directed to trust a *different, unauthenticated* field (the shop) that determines the tenant the data is applied to.

### Impact Explanation
Any merchant/attacker who can install the app on their own store (an unprivileged action available to any Shopify merchant) can capture a legitimately-signed webhook delivery for their own shop and replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to point at a victim shop. Since the gem's `Webhooks::Registry.process` validates only the body HMAC and then unconditionally dispatches the (attacker-chosen) `shop` value to the handler, this is a cross-tenant capability: the attacker can cause the host application to process data intended for one tenant as if it belongs to another tenant it does not control. Depending on which webhook topic is abused (e.g. `app/uninstalled`, `customers/redact`, `shop/redact`, or any custom topic that mutates per-shop state keyed by `shop`), this can lead to unauthorized deletion, deauthorization, or corruption of another merchant's data — cross-tenant access/impact, matching the Critical bucket in scope.

### Likelihood Explanation
The attacker only needs the ability to install the app on their own account (which any merchant can freely do) and the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint — both trivially available to an unprivileged internet user. No access token, `api_secret_key`, or privileged credential is required; the entire attack rides on a header the gem never authenticates.

### Recommendation
Include the identity-binding fields (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) in the signed material verified for webhooks, or otherwise cryptographically bind the `shop` header to the payload before trusting it (e.g., re-derive/confirm the shop from a value embedded in the signed body, or require the host application to independently confirm shop ownership before acting). At minimum, document prominently that `Registry.process`'s `shop` value is unauthenticated so host applications do not use it as a trust boundary without additional verification (e.g., cross-checking against a known/expected shop from their own session store).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook whose body they can predict/control in a way meaningful to another shop's state (e.g. a mandatory `customers/redact` or `app/uninstalled` webhook, or any custom webhook topic the app registers), capturing the raw POST:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: ...

   {}
   ```
3. Attacker resends the identical body and `x-shopify-hmac-sha256` value, but changes only the shop header:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <same-valid-hmac>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: ...

   {}
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate` computes `HMAC(Context.api_secret_key, "{}")`, which matches, per [4](#0-3) .
5. `ShopifyAPI::Webhooks::Registry.process` proceeds and invokes the registered handler with `shop: "victim-shop.myshopify.com"`, per [3](#0-2) , causing the host app to act on the victim tenant using the attacker-supplied event.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
