### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw body only, while the `shop` value used to identify which merchant/tenant the webhook belongs to is taken from an unauthenticated HTTP header and is never part of the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that header: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the raw body, using the app's shared `api_secret_key`: [2](#0-1) 

`Registry.process` treats HMAC success as full authentication of the request, then forwards `request.shop` — the unsigned header value — straight into the handler as the tenant identity: [3](#0-2) 

Because the `api_secret_key` used to compute/verify the HMAC is the app's single shared client secret (identical across every shop that installs the app), any merchant that has the app installed can capture a legitimately-signed `(body, hmac)` pair from their own store's webhook deliveries. That same `(body, hmac)` pair remains valid under `HmacValidator.validate` regardless of the `shop-domain` header value, since the header is never part of `to_signable_string`. The attacker can then resend the same body+HMAC with an arbitrary `shopify-shop-domain` header value (e.g., a victim's shop domain), and `Registry.process` will accept it as authentic and pass the forged `shop` value to the handler unquestioned.

This is exactly the class of bug described in the report's rules: a field (`shop`) that is acted upon (used as the tenant/session key passed to the handler) is not covered by the HMAC that is supposed to authenticate the request. The equality that should hold — `shop authenticated by HMAC == shop used to key handler logic/storage` — is broken, because the left side doesn't actually exist: nothing about `shop` is authenticated at all.

### Impact Explanation
A host application built on this gem typically keys per-tenant data (order sync, inventory, tokens, webhook dedup, etc.) by `WebhookMetadata#shop`, trusting it as coming from Shopify. Since any app-installing merchant can forge this value while still passing HMAC validation, this enables cross-tenant data confusion/injection into another shop's webhook processing pipeline — satisfying the "cross-tenant access" criterion for High/Critical impact.

### Likelihood Explanation
Any unprivileged user who has installed the app on their own store (a normal, non-privileged position) already possesses one or more valid `(body, hmac)` pairs from webhooks Shopify sends them, because the signature only covers the body and uses the app's single global secret. No access token, `client_secret`, or privileged access is required — only observing a webhook delivery to a store they legitimately control.

### Recommendation
Bind the claimed `shop` (and ideally `topic`/`webhook_id`) into the value that is verified, not just trusted after the fact. Options:
- Include the `shop-domain` header in `to_signable_string` so it participates in the HMAC computation, or
- Cross-check `request.shop` against a shop record/registration already known to the app for that specific webhook registration/topic (not against a value taken from the same untrusted request), before invoking the handler in `Registry.process`.

### Proof of Concept
1. App has a client secret `S`. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B` with header `x-shopify-hmac-sha256: HMAC(S, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body `B` and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC(S, B)` (the raw body, per `Request#to_signable_string`) and it matches — validation passes: [4](#0-3) 
4. `Registry.process` calls the registered handler with `shop: "victim.myshopify.com"` even though the request never proved any relationship to that shop: [5](#0-4)

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
