### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to populate `WebhookMetadata#shop`, which is handed to the host application's handler as the tenant identity for the request.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read straight from the `hmac-sha256` header: [1](#0-0) 

`HmacValidator.validate` verifies the received signature against `HMAC-SHA256(api_secret_key, raw_body)` only: [2](#0-1) 

`Registry.process` checks that HMAC and, if it passes, builds `WebhookMetadata` using `request.shop`, which comes from the `shop-domain` header — a field never included in the signed bytes: [3](#0-2) [4](#0-3) 

The equality the gem should enforce is: `shop field trusted by the handler == shop bound inside the HMAC-covered bytes`. Instead the gem enforces only `HMAC(raw_body) == HMAC(raw_body)`, leaving `shop` (and `topic`, `api_version`, `webhook_id`) completely outside the authenticated envelope. Because `api_secret_key` is one shared app secret used for *every* merchant/shop that installs the app, any unprivileged user can install the app on their own store, capture one legitimately-signed webhook delivery (valid body + valid HMAC over that body), and then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true` because it only ever re-hashes `raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` with attacker-chosen `body`.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook subsystem is supposed to provide: `WebhookMetadata#shop` is the only signal host applications have to know which merchant a webhook event belongs to, and it is exactly the field the report's bug class calls out — "a field acted on but not covered by the HMAC." A host app that keys any storage lookup, uninstall/GDPR handling, or tenant-scoped side effect off `data.shop` will process attacker-supplied data under a victim shop's identity, i.e. cross-tenant data injection/impersonation, without ever needing the victim's credentials.

### Likelihood Explanation
The prerequisite is only the ability to install the target app on any (even trial) shop to obtain one authentic `(body, hmac)` pair signed with the shared `api_secret_key`, then send a normal HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or victim credential is required — this is reachable by any unprivileged internet user who can install the app once.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`/`api_version`) into the HMAC-covered signable string, or otherwise cryptographically bind the shop identity to the signed payload (e.g., require the shop domain to be embedded in the signed body and cross-checked against the header) instead of trusting the raw header value once the body-only HMAC succeeds.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving a real webhook: `raw_body = B`, header `shopify-hmac-sha256 = HMAC(secret, B)`, `shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker resends the identical `B` and identical `hmac-sha256` value to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches — validation succeeds
( [5](#0-4) ).
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`
( [6](#0-5) ), causing the host app to process attacker-controlled data under the victim shop's tenant identity.

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
