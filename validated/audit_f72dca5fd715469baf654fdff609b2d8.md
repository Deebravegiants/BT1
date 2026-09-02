### Title
Webhook shop-domain attribution is not covered by the HMAC signature, enabling cross-tenant spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Utils::HmacValidator` authenticate a webhook delivery solely by verifying the HMAC over the raw request body, while the `shop` field that the library hands to the host application's handler (and that the app uses to attribute the event to a tenant) is read from an unauthenticated HTTP header. This breaks the identity binding `HMAC-verified bytes == data acted upon`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed payload: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` only checks `hmac` against `to_signable_string` (the body), so it never verifies the `shop` header: [3](#0-2) 

`Registry.process` accepts the request once the body-only HMAC passes, and forwards `request.shop` straight into `WebhookMetadata`, which is the value the host application's handler uses to identify the tenant (per `docs/usage/webhooks.md`, "`shop`, `String` - The shop domain of the webhook"): [4](#0-3) 

Because the `shop` header is not part of the signed bytes, the equality the library implicitly promises — "the `shop` value delivered to the handler is the shop that produced the HMAC-signed body" — does not hold. Any user who can obtain one legitimate `(raw_body, hmac)` pair generated with the app's `client_secret` (trivially available to any merchant/developer who installs the app on their own store and captures a real webhook delivery) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g. a victim shop). `HmacValidator.validate` will still succeed because it only checks the body, and `Registry.process` will dispatch to the handler with `shop` set to the attacker-chosen value.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged installer of the app (someone with a legitimate but unprivileged relationship — their own shop's webhook secret is the same shared `client_secret` used for all shops for that app) can forge the tenant attribution of an otherwise validly-signed webhook payload. Any host application that trusts `WebhookMetadata#shop` for tenant-scoped side effects (e.g. looking up a session/access token for that shop, updating per-shop state, billing, or de-duplication keyed by shop) can be made to act "as" a different, victim shop using data or triggers that never actually occurred for that shop — a cross-tenant confusion enabled purely by the gem's request/validation design, not by any app-level misuse of documented API.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs one genuine `(body, hmac)` pair signed with the app's secret — obtainable by any user who installs (or has installed) the target app on any shop and captures one real webhook delivery, then replays it to the app's public webhook endpoint with a modified `shop` header. No access to `api_secret_key`, tokens, or privileged accounts is required beyond ordinary app installation, which is the normal, unprivileged path for any merchant using the app.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the data that is cryptographically bound to the HMAC check, or, at minimum, require host applications/the gem itself to cross-check the header-derived `shop` against an independently-verified value (e.g., the shop tied to the session/webhook subscription that was registered) before dispatching to the handler, rather than trusting the raw header value implicitly labeled as authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a legitimate webhook (e.g. `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker replays that exact HTTP request to the app's webhook endpoint, but changes the `x-shopify-shop-domain` header to `victim.myshopify.com` (the body and HMAC are left untouched).
3. `ShopifyAPI::Webhooks::Request.new` parses the headers/body; `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over the unmodified raw body and it matches, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` even though the actual event occurred on `attacker.myshopify.com` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host app to attribute the (attacker-controlled) payload to the victim's tenant.

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
