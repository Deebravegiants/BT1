This confirms the analog. Let me verify `webhook_handler.rb` for how `shop` is consumed by handlers.### Title
Webhook `shop` identity is taken from an unauthenticated HTTP header, not the HMAC-covered payload, allowing cross-tenant spoofing of webhook origin - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity solely by validating the HMAC over the raw request body [1](#0-0) . The `shop` value passed to the app's `WebhookHandler` is read from the `X-Shopify-Shop-Domain` HTTP header, which is not covered by that HMAC at all [2](#0-1) [3](#0-2) . This breaks the identity binding `shop authenticated == shop the app acts on`: the HMAC proves the *body bytes* came from an app-secret holder, but says nothing about which shop the header claims to be.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate` computes/compares the signature exclusively against that signable string [4](#0-3) . Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled straight from HTTP headers via `shopify_header`, none of which participate in `to_signable_string` [5](#0-4) [6](#0-5) .

`Registry.process` raises only if the HMAC over the body fails; once that passes, it forwards `request.shop` (the unauthenticated header value) directly into the `WebhookMetadata` struct given to the host application's handler [7](#0-6) . The gem provides no cross-check that the `shop` header actually corresponds to the shop whose data produced the signed body.

Because all shops that install the same app share the exact same `client_secret`/HMAC key, any body ever legitimately signed for that app (e.g. a webhook the attacker triggered on their own store, which they fully control) is a validly-signed payload for **any** shop-domain header. Replaying that captured body to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop still passes `HmacValidator.validate`, since the header is not part of the signed bytes.

### Impact Explanation
This is a `bytes verified versus bytes parsed` / `shop authenticated versus shop stored as session key` identity-binding break as called out in scope: the gem verifies the raw body's authenticity but hands the host application a shop identifier that was never bound to that verification. A host application that (as documented and intended) uses `WebhookMetadata#shop` as the tenant key for storage lookups, session activation, or webhook processing will process attacker-supplied, attacker-shaped webhook data under a victim shop's identity — a cross-tenant data-integrity/confusion issue reachable purely through this gem's own `Registry.process`/`Request` API, without needing the app's `client_secret` or any privileged credential (the attacker only needs their own, unprivileged install of the target app to obtain one validly-signed body).

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must (1) install the same public/target app on a shop they control (a normal, unprivileged action), (2) capture one validly HMAC-signed webhook body sent to their own endpoint, and (3) replay it to the shared webhook endpoint with a forged `shop-domain` header, since HTTP headers are entirely attacker-controlled in the replayed request and the gem does not tie them to the signature.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified — either by including the shop-domain header in the signable string used for HMAC validation, or by having `Registry.process` cross-verify the header-derived shop against a shop identifier embedded in the verified body/metadata before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted as a tenant key without additional verification by the host app.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers an event that causes Shopify to send a legitimate webhook to the app's registered endpoint; the attacker captures the raw request, including `X-Shopify-Hmac-Sha256` and body.
2. Attacker resends the exact same raw body and `X-Shopify-Hmac-Sha256` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. Server code calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body:, headers:))`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only [3](#0-2)  — it matches, because the body and secret are unchanged; the forged shop header is never checked.
5. `handler.handle` receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [8](#0-7) , and the host application processes attacker-controlled webhook content under the victim shop's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
