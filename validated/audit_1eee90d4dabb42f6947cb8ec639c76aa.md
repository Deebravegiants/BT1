Now I have enough detail to confirm the finding.

### Title
Webhook `shop-domain` header is not bound by the HMAC signature, allowing cross-tenant shop spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts a completely separate, unauthenticated header (`shop-domain`) as the tenant identity handed to the host application's handler. Because the app's `client_secret` is shared across every shop that installs the app, any request with a validly-signed body can carry an attacker-chosen `shop-domain` value and still pass validation, breaking the intended binding `shop_verified == shop_processed`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` is the only authentication check performed on an inbound webhook: [1](#0-0) 

It calls `Utils::HmacValidator.validate(request)`, which recomputes the signature only from `request.to_signable_string` (the raw body) and compares it to the `hmac` header: [2](#0-1) 

`Webhooks::Request#to_signable_string` returns just `@raw_body`, and `hmac` is read from the `hmac-sha256` header. The `shop` accessor, however, is read straight from the `shop-domain` header and is never included in the signed material at all: [3](#0-2) 

After the HMAC check passes, `Registry.process` forwards this unauthenticated `request.shop` value directly into `WebhookMetadata`, which the host application's `WebhookHandler#handle` uses as the tenant/shop identity for the event: [4](#0-3) [5](#0-4) 

The `client_secret` used to compute the HMAC is the app-level secret from `Context.api_secret_key`, identical for every shop that has installed the app — it is not a per-shop secret. Consequently, a validly-signed `(body, hmac)` pair obtained from a legitimate webhook delivery for shop A remains valid when replayed with the `shop-domain` header changed to shop B: `HmacValidator.validate` only checks `hmac == HMAC(secret, body)`, it never checks that `shop-domain == body's shop`. This is precisely the analog of the reported bug class — a field (`shop`) that is acted upon (used as the tenant key passed to the handler) but not covered by the authenticity check (the HMAC), so the caller can freely control it while still passing verification.

### Impact Explanation
Any unprivileged internet user who can obtain (or is separately entitled to send, e.g. as the operator of their own trial/dev shop using the same app) one validly-signed webhook body/HMAC pair can replay it with an arbitrary `shop-domain` header. The receiving application — trusting `ShopifyAPI`'s guarantee that a webhook which passes `Registry.process` truly originates from the named shop — will process the event as if it came from a different, victim tenant. Depending on how the host app keys its data store by `data.shop` (essentially always, since that is the documented purpose of `WebhookMetadata#shop`), this enables cross-tenant data confusion/access: an attacker-controlled body (e.g. an `orders/create` or `app/uninstalled` payload) can be attributed to a victim shop of the same app, letting the attacker write, delete, or otherwise poison another tenant's records purely by supplying a spoofed header alongside a signature that Shopify's own HMAC scheme cannot distinguish, since the signing key is shared across all installs of the app rather than per-shop.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and possession of one legitimately-signed body/HMAC pair for the same app (trivially obtainable by installing the app on an attacker-controlled shop, since HMAC validation succeeds for any body signed with the shared `client_secret` regardless of which shop it was addressed to). No access token, secret leakage, or privileged account is required beyond normal, unprivileged use of the target app as an installed merchant — which matches the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` identity to the authenticated payload instead of trusting the header independently: include the `shop-domain` (and ideally `topic`/`webhook-id`) in the signable string used for HMAC verification, or otherwise cross-check the header-provided shop against a value derived from data that Shopify actually signs (e.g., validate that the shop is one for which the app currently holds an active session/token, and reject webhooks whose header shop doesn't match an expected shop from the delivery context). At minimum, document this gap and require host applications to independently verify shop ownership rather than trusting `WebhookMetadata#shop` as an authenticated value.

### Proof of Concept
1. Install the target app on an attacker-owned shop `attacker.myshopify.com`; Shopify delivers a legitimate webhook with body `B`, header `shopify-shop-domain: attacker.myshopify.com`, and `shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker replays the exact same `B` and `hmac` value to the app's webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and finds it matches the (unchanged) `hmac` header — validation passes.
4. `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` is handed to the host app's handler, which processes attacker-controlled data under the victim shop's tenant context.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
