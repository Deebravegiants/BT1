### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable string from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` to dispatch to app handlers come from unauthenticated HTTP headers. The equality that should hold — `hmac_signed_bytes == bytes_the_handler_trusts_as_belonging_to(shop)` — is broken: the HMAC binds only the body, not the `shop-domain` header that identifies the tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively over that signable string using the app's shared `api_secret_key`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as authorization to trust every other header on the request, including `request.shop`, and forwards them unchecked to the registered handler: [3](#0-2) 

Because the `api_secret_key` is the app's client secret, it is identical for every shop that installs the app — it is not a per-tenant secret. Any merchant who installs the app (an unprivileged internet user with respect to other tenants) can trigger a real webhook on their own store, capturing a raw body together with a validly computed `x-shopify-hmac-sha256` header. Since the `shop-domain` header is never included in the signed bytes, that same body+HMAC pair remains valid if the attacker replays it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to name a different, victim shop. `HmacValidator.validate` will accept the forged request because the signature check only re-derives the HMAC from `@raw_body`, and `Registry.process` will invoke the handler with `WebhookMetadata` carrying the attacker-chosen `shop` value.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: a passing HMAC check is supposed to mean "this event genuinely originates from `shop`," but `shop` is attacker-controlled while only the body is authenticated. An app that uses `data.shop` from `WebhookMetadata` to key writes, look up sessions, or drive access-controlled behavior (the intended and documented use, per `lib/shopify_api/webhooks/registry.rb:198-199`) can be made to associate attacker-supplied body content with a victim shop, i.e. cross-tenant data injection/confusion.

### Likelihood Explanation
Any user who can install the app on their own store (a normal, unprivileged onboarding action, not requiring any credential belonging to the victim or the app's `client_secret`) can generate arbitrary valid `(body, hmac)` pairs, because the app's client secret is shared across all installations and only signs the body. The only extra step is replaying the captured request with a modified `shop-domain` header, which is trivial HTTP tampering with no cryptographic material required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signable bytes, or otherwise cryptographically bind the claimed `shop` to the verified body before dispatch — e.g., validate that `request.shop` corresponds to a known, previously-established session/installation before trusting it in `Registry.process`, rather than accepting any header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`) with a body they control.
2. Attacker captures the raw POST body and the corresponding `x-shopify-hmac-sha256` header Shopify sent — both valid because they were legitimately computed with the app's shared `api_secret_key`.
3. Attacker resends this identical body and HMAC header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) recomputes the HMAC over `@raw_body` only and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds and calls the handler with `shop: "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the event never originated from that shop.

### Citations

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
